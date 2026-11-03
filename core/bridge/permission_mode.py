"""
permission_mode.py — режимы прав (как PermissionChecker в WebToApp).
Default: спрашивать. AutoApprove: всё разрешено. Plan: только чтение.
"""

import threading
from enum import Enum


class Mode(Enum):
    DEFAULT = "default"
    AUTO_APPROVE = "auto_approve"
    PLAN = "plan"


class PermissionMode:
    """Глобальное состояние режима прав. Потокобезопасно."""

    _lock = threading.RLock()
    _mode = Mode.DEFAULT

    @classmethod
    def get(cls) -> Mode:
        with cls._lock:
            return cls._mode

    @classmethod
    def set(cls, mode: Mode) -> dict:
        with cls._lock:
            cls._mode = mode
            return {"ok": True, "mode": mode.value}

    @classmethod
    def set_by_name(cls, name: str) -> dict:
        try:
            mode = Mode(name.lower())
        except ValueError:
            return {"ok": False, "error": f"Unknown mode: {name}. Use default/auto_approve/plan"}
        return cls.set(mode)

    @classmethod
    def status(cls) -> dict:
        with cls._lock:
            return {"mode": cls._mode.value}

    @classmethod
    def is_auto_approve(cls) -> bool:
        with cls._lock:
            return cls._mode == Mode.AUTO_APPROVE

    @classmethod
    def is_plan(cls) -> bool:
        with cls._lock:
            return cls._mode == Mode.PLAN
