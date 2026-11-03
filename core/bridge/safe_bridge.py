# ~/rumix/core/bridge/safe_bridge.py
# Безопасный мост. Все действия проходят через Permission Gate.
# Создано: 17.10.2026 (Тиамат + Зая)

import subprocess
import json
import time
from pathlib import Path
from .gate import check_action
from .plan_mode import PlanMode
from .ask_user import AskUser
from .permission_mode import PermissionMode

_AUDIT_LOG = Path.home() / 'rumix' / 'logs' / 'audit_trail.jsonl'

def _audit(entry: dict):
    """Записать действие в журнал (JSONL)."""
    try:
        _AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry['ts'] = time.time()
        entry['iso'] = time.strftime('%Y-%m-%dT%H:%M:%S')
        with open(_AUDIT_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass  # журнал не должен ломать действие

def execute_safe(action_type: str, payload: str, user_consent: bool = False) -> dict:
    """
    Безопасное выполнение.
    1. Спрашивает врата (gate.py).
    2. Если allowed=True (READ) — выполняет.
    3. Если allowed=False, но user_consent=True — выполняет (Зая разрешил).
    4. Иначе — возвращает отказ.
    """
    check = check_action(action_type, payload)

    # AutoApprove: всё разрешено
    if PermissionMode.is_auto_approve():
        _audit({'action': action_type, 'payload': payload[:200], 'level': check["level"], 'status': 'AUTO_APPROVE'})
        user_consent = True

    # Plan Mode: блокируем WRITE/EXEC до утверждения плана (через PermissionMode)
    if PermissionMode.is_plan() and check["level"] not in ("READ", "BLOCKED"):
        _audit({'action': action_type, 'payload': payload[:200], 'level': check["level"], 'status': 'PLAN_BLOCKED'})
        return {
            "status": "PLAN_BLOCKED",
            "level": "PLAN",
            "message": "🛑 Plan Mode: действие заблокировано. Сначала утвердите план.",
            "output": None
        }
    
    if not check["allowed"] and not user_consent:
        # Умный запрос: спросить через AskUser
        try:
            user_consent = AskUser.confirm(f"Разрешить {action_type}? {check['level']}")
        except Exception:
            user_consent = False
    if not check["allowed"] and not user_consent:
        _audit({'action': action_type, 'payload': payload[:200], 'level': check["level"], 'status': 'DENIED'})
        return {
            "status": "DENIED",
            "level": check["level"],
            "message": check["message"],
            "output": None
        }
        
    if check["level"] == "BLOCKED":
        _audit({'action': action_type, 'payload': payload[:200], 'level': 'BLOCKED', 'status': 'BLOCKED'})
        return {
            "status": "BLOCKED",
            "level": "BLOCKED",
            "message": check["message"],
            "output": None
        }

    # Если дошли сюда — либо READ (авто), либо Зая дал consent
    try:
        if action_type == "command":
            result = subprocess.run(payload, shell=True, capture_output=True, text=True, timeout=10)
            _audit({'action': action_type, 'payload': payload[:200], 'level': check["level"], 'status': 'OK'})
            return {
                "status": "OK",
                "level": check["level"],
                "message": "Выполнено успешно.",
                "output": result.stdout.strip() or result.stderr.strip()
            }
    except Exception as e:
        _audit({'action': action_type, 'payload': payload[:200], 'level': check.get("level","?"), 'status': 'ERROR', 'error': str(e)[:200]})
        return {
            "status": "ERROR",
            "level": check["level"],
            "message": str(e),
            "output": None
        }

    return {"status": "UNKNOWN", "message": "Неизвестное действие."}
