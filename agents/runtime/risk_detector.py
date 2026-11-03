#!/data/data/com.termux/files/usr/bin/env python3
"""
risk_detector.py — детектор опасных команд (порт из Ultra + градация).

3 уровня: HIGH / MEDIUM / LOW.
HIGH — блок.
MEDIUM — спросить.
LOW — allow.
"""

import re
from enum import Enum


class RiskType(Enum):
    DD = "dd запись"
    SU_SUDO = "su/sudo"
    FORMAT = "форматирование"
    RM_RF_ROOT = "rm -rf root"
    FORK_BOMB = "fork bomb"
    KERNEL_MODULE = "kernel module"
    RAW_DISK_WRITE = "raw disk write"
    SHUTDOWN_REBOOT = "shutdown/reboot"
    SETPROP = "setprop"
    ROOT_CMD = "root cmd"
    RM = "rm"
    MV = "mv"
    CHMOD = "chmod"
    CHOWN = "chown"
    KILL = "kill"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


MAX_DETECT_INPUT = 8 * 1024


PATTERNS = [
    # HIGH
    (re.compile(r'\bdd\b\s+[^\n;|&]*of=/dev/(?:null|zero|random|urandom|(?:sd[a-z]|nvme\d+n\d+|mmcblk\d+|loop\d+|ram\d+|zram\d+|vd[a-z]|xvd[a-z]|blk\d+)(?:p?\d*)?)', re.I),
     RiskType.DD, "dd пишет в устройство", RiskLevel.HIGH, False),
    (re.compile(r'\bdd\b\s+[^\n;|&]*\|\s*dd\b\s+[^\n;|&]*of=/dev/', re.I),
     RiskType.DD, "dd через pipe", RiskLevel.HIGH, False),
    (re.compile(r'\bdd\b', re.I),
     RiskType.DD, "dd — может перезаписать", RiskLevel.HIGH, False),
    (re.compile(r'(?:^|[;|&])\s*(?:su|sudo)\b'),
     RiskType.SU_SUDO, "su/sudo", RiskLevel.HIGH, True),
    (re.compile(r'\b(mkfs(?:\.[a-z0-9]+)?|newfs(?:_msdos)?)\b', re.I),
     RiskType.FORMAT, "mkfs", RiskLevel.HIGH, False),
    (re.compile(r'\b(fdisk|parted|sfdisk|cfdisk|gdisk|sgdisk)\b', re.I),
     RiskType.FORMAT, "разметка", RiskLevel.HIGH, False),
    (re.compile(r'\brm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+|--recursive\s+)(?:/\s*$|/\*\s*$|/(?:etc|bin|sbin|usr|var|lib|home|root|system|vendor|product|odm|data|mnt|sdcard|boot|proc|sys)\b)'),
     RiskType.RM_RF_ROOT, "rm -rf корень", RiskLevel.HIGH, False),
    (re.compile(r':\(\)\{\s*:\s*\|\s*:\s*&\s*\}\s*;?\s*'),
     RiskType.FORK_BOMB, "fork bomb", RiskLevel.HIGH, False),
    (re.compile(r'\bfork\s*bomb\b', re.I),
     RiskType.FORK_BOMB, "fork bomb", RiskLevel.HIGH, False),
    (re.compile(r'\b(insmod|rmmod|modprobe|modinfo|lsmod)\b', re.I),
     RiskType.KERNEL_MODULE, "модули ядра", RiskLevel.HIGH, False),
    (re.compile(r'\b(?:cat|cp|pv|tee|gunzip|gzip|bzip2|xz|zstd)\b[^\n;|]*>\s*/dev/(?:sd[a-z]|nvme\d+n\d+|mmcblk\d+|loop\d+|ram\d+|zram\d+|vd[a-z]|xvd[a-z]|blk\d+)', re.I),
     RiskType.RAW_DISK_WRITE, "запись в блочное устройство", RiskLevel.HIGH, False),
    (re.compile(r'^\s*(?:shutdown|reboot|poweroff|halt|init\s+[06])\b', re.I),
     RiskType.SHUTDOWN_REBOOT, "выключение", RiskLevel.HIGH, False),
    (re.compile(r'^\s*format\s+[a-zA-Z]:', re.I),
     RiskType.FORMAT, "Windows format", RiskLevel.HIGH, False, True),
    (re.compile(r'^\s*diskpart\b', re.I),
     RiskType.FORMAT, "diskpart", RiskLevel.HIGH, False, True),
    (re.compile(r'^\s*bcdedit\b', re.I),
     RiskType.FORMAT, "bcdedit", RiskLevel.HIGH, False, True),
    (re.compile(r'\bsetprop\s+(?:persist\.|ro\.|sys\.)', re.I),
     RiskType.SETPROP, "setprop системных свойств", RiskLevel.HIGH, True),
    (re.compile(r'\bchmod\s+(-[a-zA-Z]*\s+)?777\b', re.I),
     RiskType.ROOT_CMD, "chmod 777", RiskLevel.HIGH, True),
    (re.compile(r'\b(?:mount|remount)\s+(?:-o\s+)?(?:rw|ro|noatime)\s+/(?:system|vendor|product|odm)', re.I),
     RiskType.ROOT_CMD, "mount системного раздела", RiskLevel.HIGH, True),
    (re.compile(r'\b(?:setenforce|selinuxenabled|getenforce)\b', re.I),
     RiskType.ROOT_CMD, "SELinux", RiskLevel.HIGH, True),

    # MEDIUM
    (re.compile(r'\brm\s', re.I),
     RiskType.RM, "rm", RiskLevel.MEDIUM, False),
    (re.compile(r'\bmv\s', re.I),
     RiskType.MV, "mv", RiskLevel.MEDIUM, False),
    (re.compile(r'\bchmod\s', re.I),
     RiskType.CHMOD, "chmod", RiskLevel.MEDIUM, False),
    (re.compile(r'\bchown\s', re.I),
     RiskType.CHOWN, "chown", RiskLevel.MEDIUM, False),
    (re.compile(r'\b(?:kill|killall|pkill)\s', re.I),
     RiskType.KILL, "kill", RiskLevel.MEDIUM, False),
    (re.compile(r'\bformat\b', re.I),
     RiskType.FORMAT, "format", RiskLevel.MEDIUM, False),
]


class RiskResult:
    def __init__(self, is_dangerous, risk_type=None, matched="", description="",
                 risk_level=RiskLevel.LOW, is_windows=False):
        self.is_dangerous = is_dangerous
        self.risk_type = risk_type
        self.matched_command = matched
        self.description = description
        self.risk_level = risk_level
        self.is_windows_disk_command = is_windows

    def to_dict(self):
        return {
            "is_dangerous": self.is_dangerous,
            "risk_type": self.risk_type.value if self.risk_type else None,
            "matched_command": self.matched_command,
            "description": self.description,
            "risk_level": self.risk_level.value,
            "is_windows_disk_command": self.is_windows_disk_command,
        }


def detect(command, is_native=True):
    """
    Проверить команду на опасность.
    is_native: True — Termux, False — контейнер.
    Возвращает RiskResult с risk_level: HIGH / MEDIUM / LOW.
    """
    if not command or not isinstance(command, str):
        return RiskResult(False)

    if len(command) > MAX_DETECT_INPUT:
        command = command[:MAX_DETECT_INPUT]

    best = RiskResult(False)
    best_rank = 0

    for entry in PATTERNS:
        pattern = entry[0]
        risk_type = entry[1]
        description = entry[2]
        risk_level = entry[3]
        require_native = entry[4] if len(entry) > 4 else False
        is_windows = entry[5] if len(entry) > 5 else False

        if require_native and not is_native:
            continue

        m = pattern.search(command)
        if m:
            rank = {RiskLevel.HIGH: 3, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 1}[risk_level]
            if rank > best_rank:
                best_rank = rank
                best = RiskResult(True, risk_type, m.group(0)[:200], description, risk_level, is_windows)

    return best


if __name__ == "__main__":
    tests = [
        "ls -la",
        "rm file.txt",
        "chmod 644 file.txt",
        "rm -rf /",
        "dd if=/dev/zero of=/dev/sda",
        "mkfs.ext4 /dev/sda1",
        "sudo apt update",
        "chmod 777 /etc",
        "format C:",
        ":(){ :|:& };:",
    ]
    for t in tests:
        r = detect(t)
        if r.is_dangerous:
            status = f"⚠️  {r.risk_level.value.upper()}"
        else:
            status = "✅ safe"
        print(f"{status}: {t}  ->  {r.description if r.is_dangerous else ''}")
