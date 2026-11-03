"""
registry.py — глобальный реестр файловых систем.
Порт из Twig (core-fs/src/main/kotlin/com/twig/core/FsRegistry.kt).

scheme → FileSystem. Потокобезопасно.
Каждый модуль (fs_local, fs_zip, ...) регистрирует себя при инициализации.
"""

import threading
from typing import Dict, List, Optional

from .filesystem import FileSystem
from .xfile import XFile
from .fs_exception import FsException


class FsRegistry:
    """Глобальный реестр scheme → FileSystem. Потокобезопасный, с порядком регистрации."""

    _lock = threading.RLock()
    _systems: Dict[str, FileSystem] = {}

    @classmethod
    def register(cls, fs: FileSystem) -> None:
        """Зарегистрировать файловую систему под её scheme."""
        with cls._lock:
            cls._systems[fs.scheme] = fs

    @classmethod
    def unregister(cls, scheme: str) -> Optional[FileSystem]:
        """Убрать схему, вернуть удалённую ФС или None."""
        with cls._lock:
            return cls._systems.pop(scheme, None)

    @classmethod
    def of(cls, key) -> FileSystem:
        """Найти ФС по scheme (str) или по XFile."""
        scheme = key.scheme if isinstance(key, XFile) else key
        with cls._lock:
            fs = cls._systems.get(scheme)
        if fs is None:
            raise FsException(f"No file system registered for scheme: {scheme}")
        return fs

    @classmethod
    def all(cls) -> List[FileSystem]:
        """Все зарегистрированные ФС в порядке регистрации."""
        with cls._lock:
            return list(cls._systems.values())
