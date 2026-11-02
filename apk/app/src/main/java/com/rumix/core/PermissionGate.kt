package com.rumix.core

enum class GateLevel { BLOCKED, READ, WRITE, EXEC, UNKNOWN }

data class GateDecision(
    val allowed: Boolean,
    val level: GateLevel,
    val message: String,
    val needsConsent: Boolean = false,
    val whitelisted: Boolean = false,
)

object PermissionGate {

    private val DANGEROUS_CHARS = charArrayOf(';', '&', '|', '$', '(', ')', '`')

    private val DANGEROUS_PATTERNS = listOf(
        Regex("""rm\\s+-rf\\s+/"""),
        Regex("""mkfs"""),
        Regex("""dd\\s+if="""),
        Regex("""\\:\\(\\)\\s*\\{\\s*:\\|:&\\s*\\}\\;:"""),
        Regex("""chmod\\s+-R\\s+777"""),
        Regex(""">\\s*/dev/sda"""),
        Regex("""curl.*\\|\\s*sh"""),
        Regex("""wget.*\\|\\s*sh"""),
    )

    private val READ_BASE = setOf("ls", "cat", "pwd", "echo", "grep", "wc", "head", "tail", "less")

    val EXEC_WHITELIST = setOf(
        "clear", "ls", "cat", "pwd", "echo", "grep", "wc",
        "git", "pgrep", "ps", "df", "du", "free", "uptime",
        "sv", "whoami", "id", "date", "uname", "getprop", "env",
        "head", "tail", "less",
    )

    private val SENSITIVE = listOf(".env", "id_rsa", ".git/config", "passwd", "shadow")

    fun classifyCommand(raw: String): GateDecision {
        val cmd = raw.trim()
        if (cmd.isEmpty()) return GateDecision(false, GateLevel.UNKNOWN, "Пустая команда")

        for (ch in DANGEROUS_CHARS) {
            if (ch in cmd) {
                return GateDecision(false, GateLevel.BLOCKED, "🚫 Заблокировано: опасный символ «$ch» в команде")
            }
        }
        for (p in DANGEROUS_PATTERNS) {
            if (p.containsMatchIn(cmd)) {
                return GateDecision(false, GateLevel.BLOCKED, "🚫 Заблокировано: опасный паттерн")
            }
        }

        val base = cmd.split(Regex("""\\s+""")).firstOrNull().orEmpty()
        if (base.isEmpty()) return GateDecision(false, GateLevel.UNKNOWN, "Неизвестная команда")

        if (base in READ_BASE) {
            return GateDecision(true, GateLevel.READ, "✅ Чтение разрешено (авто)")
        }
        if (base in EXEC_WHITELIST) {
            return GateDecision(true, GateLevel.EXEC, "✅ EXEC из белого списка", whitelisted = true)
        }
        return GateDecision(false, GateLevel.EXEC, "🛑 EXEC: требуется согласие Зая", needsConsent = true)
    }

    fun checkFile(path: String, mode: String = "read"): GateDecision {
        for (s in SENSITIVE) {
            if (s in path) {
                return GateDecision(false, GateLevel.BLOCKED, "🚫 Доступ запрещён (секрет/системный): $path")
            }
        }
        return when (mode) {
            "read" -> GateDecision(true, GateLevel.READ, "✅ Чтение файла разрешено: $path")
            "write" -> GateDecision(false, GateLevel.WRITE, "🛑 Запись в файл требует разрешения: $path")
            else -> GateDecision(false, GateLevel.UNKNOWN, "Неизвестный режим")
        }
    }
}
