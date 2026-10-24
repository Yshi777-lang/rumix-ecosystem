#!/data/data/com.termux/files/usr/bin/env python3
"""
permissions.py — Permission Gate (3 уровня риска).

READ     → automatic
WRITE    → approval
EXEC     → HIGH блок, MEDIUM consent, LOW auto
NETWORK  → approval / policy
"""

from enum import Enum

try:
    from runtime.risk_detector import detect as risk_detect, RiskLevel
    HAS_RISK = True
except ImportError:
    HAS_RISK = False


class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXEC = "exec"
    NETWORK = "network"


AUTO_APPROVE = {Permission.READ}


def check(tool_name, permissions, auto_approve=False, command=None):
    """
    Проверить, разрешено ли выполнение tool.
    auto_approve: True — пропустить.
    command: команда для risk_detector (если есть).
    """
    if auto_approve:
        perms = ",".join(p.value for p in permissions)
        print(f"⚠️  [PERM] {tool_name}: {perms} (auto-approved)")
        return True

    for perm in permissions:
        if perm in AUTO_APPROVE:
            continue

        # EXEC + command → проверка через risk_detector с градацией
        if perm == Permission.EXEC and command and HAS_RISK:
            result = risk_detect(command)
            if result.risk_level == RiskLevel.HIGH:
                raise PermissionError(
                    f"{tool_name}: EXEC HIGH — {result.description}"
                )
            if result.risk_level == RiskLevel.MEDIUM:
                prompt = f"🔐 {tool_name}: MEDIUM ({result.description}). Разрешить? (y/N): "
                answer = input(prompt).strip().lower()
                if answer != "y":
                    raise PermissionError(f"{tool_name}: MEDIUM отклонено")
                continue
            if result.risk_level == RiskLevel.LOW:
                print(f"⚠️  [RISK] {tool_name}: команда LOW — {command[:60]}")
                continue

        # WRITE / EXEC / NETWORK — спросить
        prompt = f"🔐 {tool_name} требует {perm.value}. Разрешить? (y/N): "
        answer = input(prompt).strip().lower()
        if answer != "y":
            raise PermissionError(f"{tool_name}: {perm.value} отклонено пользователем")

    return True
