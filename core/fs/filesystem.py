"""
filesystem.py — контракт файловой системы.
Порт из Twig (core-fs/src/main/kotlin/com/twig/core/FileSystem.kt).

Правила:
- resolve() — только навигация, не для проверки существования.
- Ошибки — FsException, не None.
- list() — директории вперёд, потом по имени (case-insensitive).
- Все методы блокирующие: вызывающий сам решает про потоки.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, BinaryIO

from .xfile import XFile
from .fs_exception import FsException


class FileSystem(ABC):
    """Провайдер файловой системы. Один на local, zip, ftp, smb и т.д."""

    @property
    @abstractmethod
    def scheme(self) -> str:
        """Уникальная схема, соответствует XFile.scheme (например, 'file')."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Человекочитаемое имя для сайдбара ('Local', 'Archive')."""
        ...

    @abstractmethod
    def root(self) -> XFile:
        """Корневая запись этой ФС."""
        ...

    @abstractmethod
    def resolve(self, path: str) -> XFile:
        """
        Путь → запись. Для навигации.
        Не использовать для проверки существования — для этого stat().
        """
        ...

    @abstractmethod
    def stat(self, path: str) -> Optional[XFile]:
        """Честный stat: запись или None, если не существует."""
        ...

    @abstractmethod
    def list(self, directory: XFile) -> List[XFile]:
        """Список записей в директории. Папки вперёд, потом по имени."""
        ...

    @abstractmethod
    def open_input(self, file: XFile) -> BinaryIO:
        """Открыть поток чтения. Вызывающий закрывает."""
        ...

    @abstractmethod
    def open_output(self, file: XFile, append: bool = False) -> BinaryIO:
        """Открыть поток записи. Создать, если нет. Вызывающий закрывает."""
        ...
