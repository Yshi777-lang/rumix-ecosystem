# ~/rumix/core/bridge/permissions.py
# Permission Gate — уровни доступа и белый список.
# Создано: 17.10.2026 (Тиамат + Зая)

import os
import re

class PermissionLevel:
    READ = "READ"    # 🟢 Авто
    WRITE = "WRITE"  # 🟡 Спросить
    EXEC = "EXEC"    # 🔴 Спросить + whitelist

# Разрешённые команды (EXEC)
EXEC_WHITELIST = [
    "clear",
    "ls", "cat", "pwd", "echo", "grep", "wc",
    "git status", "git log", "git diff", "git branch",
    "pgrep", "ps", "df", "du", "free", "uptime",
    "sv status", "sv restart",
]

# Опасные паттерны (автоматический блок)
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"mkfs",
    r"dd\s+if=",
    r":\(\)\s*\{\s*:\|:&\s*\};:", # fork bomb
    r"chmod\s+-R\s+777",
    r">\s*/dev/sda",
    r"curl.*\|\s*sh",
    r"wget.*\|\s*sh",
]

def classify_command(cmd: str) -> str:
    """Определяет уровень риска. Блокирует ; && || | $ ( ) и обратные кавычки."""
    cmd = cmd.strip()

    # 0. Опасные символы (цепочки, подстановки)
    dangerous_chars = [';', '&', '|', '$', '(', ')', '`']
    for ch in dangerous_chars:
        if ch in cmd:
            return "BLOCKED"

    # 1. Проверка на опасные паттерны
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd):
            return "BLOCKED"

    # 2. Только одно слово (без пробелов) — проверяем whitelist
    parts = cmd.split()
    if len(parts) == 0:
        return PermissionLevel.EXEC

    base = parts[0]
    if base in ["ls", "cat", "pwd", "echo", "grep", "wc", "head", "tail", "less"]:
        return PermissionLevel.READ

    # 3. Всё остальное — EXEC (требует спроса)
    return PermissionLevel.EXEC

def check_file_access(path: str, mode: str) -> bool:
    """Проверка доступа к файлу."""
    # Пока простая логика: запрет на .env, секреты, системные файлы
    sensitive = [".env", "id_rsa", ".git/config", "passwd", "shadow"]
    for s in sensitive:
        if s in path:
            return False
    return True
