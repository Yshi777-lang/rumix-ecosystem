package com.rumix.core

enum class RiskLevel { LOW, MEDIUM, HIGH }

data class RiskResult(
    val isDangerous: Boolean = false,
    val type: String = "",
    val matched: String = "",
    val description: String = "",
    val level: RiskLevel = RiskLevel.LOW,
    val isWindows: Boolean = false,
)

object RiskDetector {

    private const val MAX_INPUT = 8 * 1024

    private class Rule(
        val re: Regex,
        val type: String,
        val desc: String,
        val level: RiskLevel,
        val nativeOnly: Boolean = false,
        val windows: Boolean = false,
    )

    private fun rx(p: String, ignoreCase: Boolean = true): Regex =
        Regex(p, if (ignoreCase) setOf(RegexOption.IGNORE_CASE) else emptySet())

    private val RULES: List<Rule> = listOf(
        Rule(rx("""\\bdd\\b\\s+[^\\n;|&]*of=/dev/(?:null|zero|random|urandom|(?:sd[a-z]|nvme\\d+n\\d+|mmcblk\\d+|loop\\d+|ram\\d+|zram\\d+|vd[a-z]|xvd[a-z]|blk\\d+)(?:p?\\d*)?)"""),
            "dd запись", "dd пишет в устройство", RiskLevel.HIGH),
        Rule(rx("""\\bdd\\b\\s+[^\\n;|&]*\\|\\s*dd\\b\\s+[^\\n;|&]*of=/dev/"""),
            "dd запись", "dd через pipe", RiskLevel.HIGH),
        Rule(rx("""\\bdd\\b"""), "dd запись", "dd — может перезаписать", RiskLevel.HIGH),
        Rule(rx("""(?:^|[;|&])\\s*(?:su|sudo)\\b""", ignoreCase = false),
            "su/sudo", "su/sudo", RiskLevel.HIGH, nativeOnly = true),
        Rule(rx("""\\b(mkfs(?:\\.[a-z0-9]+)?|newfs(?:_msdos)?)\\b"""),
            "форматирование", "mkfs", RiskLevel.HIGH),
        Rule(rx("""\\b(fdisk|parted|sfdisk|cfdisk|gdisk|sgdisk)\\b"""),
            "форматирование", "разметка", RiskLevel.HIGH),
        Rule(rx("""\\brm\\s+(-[a-zA-Z]*r[a-zA-Z]*\\s+|--recursive\\s+)(?:/\\s*$|/\\*\\s*$|/(?:etc|bin|sbin|usr|var|lib|home|root|system|vendor|product|odm|data|mnt|sdcard|boot|proc|sys)\\b)"""),
            "rm -rf root", "rm -rf корень", RiskLevel.HIGH),
        Rule(rx("""\\:\\(\\)\\{\\s*:\\s*\\|\\s*:\\s*&\\s*\\}\\s*;?\\s*""", ignoreCase = false),
            "fork bomb", "fork bomb", RiskLevel.HIGH),
        Rule(rx("""\\bfork\\s+bomb\\b"""), "fork bomb", "fork bomb", RiskLevel.HIGH),
        Rule(rx("""\\b(insmod|rmmod|modprobe|modinfo|lsmod)\\b"""),
            "модули ядра", "модули ядра", RiskLevel.HIGH),
        Rule(rx("""\\b(?:cat|cp|pv|tee|gunzip|gzip|bzip2|xz|zstd)\\b[^\\n;|]*>\\s*/dev/(?:sd[a-z]|nvme\\d+n\\d+|mmcblk\\d+|loop\\d+|ram\\d+|zram\\d+|vd[a-z]|xvd[a-z]|blk\\d+)"""),
            "raw disk write", "запись в блочное устройство", RiskLevel.HIGH),
        Rule(rx("""^\\s*(?:shutdown|reboot|poweroff|halt|init\\s+[06])\\b"""),
            "shutdown/reboot", "выключение", RiskLevel.HIGH),
        Rule(rx("""^\\s*format\\s+[a-zA-Z]:"""), "форматирование", "Windows format", RiskLevel.HIGH, windows = true),
        Rule(rx("""^\\s*diskpart\\b"""), "форматирование", "diskpart", RiskLevel.HIGH, windows = true),
        Rule(rx("""^\\s*bcdedit\\b"""), "форматирование", "bcdedit", RiskLevel.HIGH, windows = true),
        Rule(rx("""\\bsetprop\\s+(?:persist\\.|ro\\.|sys\\.)"""), "setprop", "setprop системных свойств", RiskLevel.HIGH, nativeOnly = true),
        Rule(rx("""\\bchmod\\s+(-[a-zA-Z]*\\s+)?777\\b"""), "root cmd", "chmod 777", RiskLevel.HIGH, nativeOnly = true),
        Rule(rx("""\\b(?:mount|remount)\\s+(?:-o\\s+)?(?:rw|ro|noatime)\\s+/(?:system|vendor|product|odm)"""),
            "root cmd", "mount системного раздела", RiskLevel.HIGH, nativeOnly = true),
        Rule(rx("""\\b(?:setenforce|selinuxenabled|getenforce)\\b"""), "root cmd", "SELinux", RiskLevel.HIGH, nativeOnly = true),
        Rule(rx("""\\brm\\s"""), "rm", "rm", RiskLevel.MEDIUM),
        Rule(rx("""\\bmv\\s"""), "mv", "mv", RiskLevel.MEDIUM),
        Rule(rx("""\\bchmod\\s"""), "chmod", "chmod", RiskLevel.MEDIUM),
        Rule(rx("""\\bchown\\s"""), "chown", "chown", RiskLevel.MEDIUM),
        Rule(rx("""\\b(?:kill|killall|pkill)\\s"""), "kill", "kill", RiskLevel.MEDIUM),
        Rule(rx("""\\bformat\\b"""), "форматирование", "format", RiskLevel.MEDIUM),
    )

    private fun rank(l: RiskLevel): Int = when (l) {
        RiskLevel.HIGH -> 3
        RiskLevel.MEDIUM -> 2
        RiskLevel.LOW -> 1
    }

    fun detect(command: String?, isNative: Boolean = true): RiskResult {
        if (command.isNullOrBlank()) return RiskResult()
        val cmd = if (command.length > MAX_INPUT) command.substring(0, MAX_INPUT) else command

        var best = RiskResult()
        var bestRank = 0
        for (rule in RULES) {
            if (rule.nativeOnly && !isNative) continue
            val m = rule.re.find(cmd) ?: continue
            if (rank(rule.level) > bestRank) {
                bestRank = rank(rule.level)
                best = RiskResult(
                    isDangerous = true,
                    type = rule.type,
                    matched = m.value.take(200),
                    description = rule.desc,
                    level = rule.level,
                    isWindows = rule.windows,
                )
            }
        }
        return best
    }
}
