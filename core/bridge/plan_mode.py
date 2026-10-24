"""
plan_mode.py — режим планирования в Permission Gate.
Аналог PlanManager из WebToApp, упрощённый.

Когда Plan Mode включён:
- READ разрешено.
- WRITE/EXEC — ЗАПРЕЩЕНЫ до approve().
"""

import threading


class PlanMode:
    """Глобальное состояние Plan Mode. Потокобезопасно."""

    _lock = threading.RLock()
    _active = False
    _plan_file = None

    @classmethod
    def enter(cls, plan_file: str = None) -> dict:
        """Включить Plan Mode. Возвращает статус."""
        with cls._lock:
            if cls._active:
                return {"ok": False, "message": "Plan Mode уже активен", "plan_file": cls._plan_file}
            cls._active = True
            cls._plan_file = plan_file
            return {"ok": True, "message": "Plan Mode включён", "plan_file": plan_file}

    @classmethod
    def exit(cls) -> dict:
        """Выключить Plan Mode (без утверждения)."""
        with cls._lock:
            cls._active = False
            cls._plan_file = None
            return {"ok": True, "message": "Plan Mode выключен"}

    @classmethod
    def approve(cls) -> dict:
        """Утвердить план и выключить Plan Mode."""
        with cls._lock:
            cls._active = False
            cls._plan_file = None
            return {"ok": True, "message": "План утверждён. Plan Mode выключен."}

    @classmethod
    def is_active(cls) -> bool:
        with cls._lock:
            return cls._active

    @classmethod
    def status(cls) -> dict:
        with cls._lock:
            return {"active": cls._active, "plan_file": cls._plan_file}
