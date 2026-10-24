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
    """Определяет уровень риска для команды."""
    cmd = cmd.strip()
    
    # 1. Проверка на опасные паттерны
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd):
            return "BLOCKED"
    
    # 2. Проверка whitelist
    for allowed in EXEC_WHITELIST:
        if cmd == allowed or cmd.startswith(allowed + " "):
            return PermissionLevel.READ if allowed in ["ls", "cat", "pwd", "echo", "grep", "wc"] else PermissionLevel.EXEC

    # 3. Если не в whitelist, но похоже на чтение
    if cmd.split()[0] in ["ls", "cat", "head", "tail", "less", "grep", "wc"]:
        return PermissionLevel.READ
        
    # 4. Всё остальное — EXEC (требует спроса)
    return PermissionLevel.EXEC

def check_file_access(path: str, mode: str) -> bool:
    """Проверка доступа к файлу."""
    # Пока простая логика: запрет на .env, секреты, системные файлы
    sensitive = [".env", "id_rsa", ".git/config", "passwd", "shadow"]
    for s in sensitive:
        if s in path:
            return False
    return True
