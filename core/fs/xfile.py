"""
xfile.py — универсальный дескриптор файла.
Порт из Twig (core-fs/src/main/kotlin/com/twig/core/XFile.kt).
Иммутабельный, без IO. Только данные и вычисляемые свойства.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class XFile:
    """
    Единая "запись" — локальный файл, элемент в архиве, файл на FTP,
    объект в облаке. Для UI любой источник — это XFile.
    Какой FileSystem его интерпретирует — решает scheme.
    """
    scheme: str
    path: str
    is_dir: bool
    size: int = 0
    last_modified: float = 0.0
    can_read: bool = True
    can_write: bool = True
    display_name: Optional[str] = None

    @property
    def name(self) -> str:
        """Имя файла: display_name, иначе последний сегмент path. Для корня — '/'."""
        if self.display_name:
            return self.display_name
        if self.path in ("/", ""):
            return "/"
        trimmed = self.path.rstrip("/")
        idx = trimmed.rfind("/")
        return trimmed if idx < 0 else trimmed[idx + 1:]

    @property
    def parent_path(self) -> str:
        """Путь родителя. Родитель корня — корень."""
        if self.path in ("/", ""):
            return "/"
        trimmed = self.path.rstrip("/")
        idx = trimmed.rfind("/")
        return "/" if idx <= 0 else trimmed[:idx]

    @property
    def extension(self) -> str:
        """Расширение в нижнем регистре, без точки. Пустая строка, если нет."""
        n = self.name
        dot = n.rfind(".")
        return "" if dot <= 0 else n[dot + 1:].lower()
