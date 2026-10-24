"""
fs_local.py — локальная файловая система.
Порт из Twig (fs-local/.../LocalFileSystem.kt), упрощённый под Termux.

Без PrivilegedFs и SAF — в Termux у нас shell и права.
"""

import os
from pathlib import Path
from typing import BinaryIO, List, Optional

from .filesystem import FileSystem
from .xfile import XFile
from .fs_exception import FsException


class LocalFileSystem(FileSystem):
    """Локальные файлы через os.scandir + pathlib + open()."""

    def __init__(self, root_dir: str = "/", display_name: str = "Local"):
        self._root_dir = root_dir
        self._display_name = display_name

    @property
    def scheme(self) -> str:
        return "file"

    @property
    def display_name(self) -> str:
        return self._display_name

    def _to_xfile(self, path: str) -> XFile:
        p = Path(path)
        try:
            st = p.stat()
            is_dir = p.is_dir()
            size = st.st_size if not is_dir else 0
            mtime = st.st_mtime
            can_read = os.access(path, os.R_OK)
            can_write = os.access(path, os.W_OK)
        except (OSError, PermissionError):
            is_dir = False
            size = 0
            mtime = 0.0
            can_read = True
            can_write = True
        return XFile(
            scheme=self.scheme,
            path=str(path),
            is_dir=is_dir,
            size=size,
            last_modified=mtime,
            can_read=can_read,
            can_write=can_write,
            display_name=None,
        )

    def root(self) -> XFile:
        return self._to_xfile(self._root_dir)

    def resolve(self, path: str) -> XFile:
        if not Path(path).exists():
            raise FsException(f"No such path: {path}")
        return self._to_xfile(path)

    def stat(self, path: str) -> Optional[XFile]:
        if not Path(path).exists():
            return None
        return self._to_xfile(path)

    def list(self, directory: XFile) -> List[XFile]:
        if not directory.is_dir:
            raise FsException(f"Not a directory: {directory.path}")
        try:
            entries = list(os.scandir(directory.path))
        except (OSError, PermissionError) as e:
            raise FsException(f"Cannot read directory: {directory.path} ({e})")
        items = [self._to_xfile(e.path) for e in entries]
        return sorted(items, key=lambda f: (not f.is_dir, f.name.lower()))

    def walk(self, directory: XFile, max_depth: int = 3):
        """Обход дерева до max_depth. yield XFile."""
        if max_depth <= 0:
            return
        try:
            for item in self.list(directory):
                yield item
                if item.is_dir and max_depth > 1:
                    yield from self.walk(item, max_depth - 1)
        except FsException:
            return

    def open_input(self, file: XFile) -> BinaryIO:
        try:
            return open(file.path, "rb")
        except (OSError, PermissionError) as e:
            raise FsException(f"Cannot read: {file.path} ({e})")

    def open_output(self, file: XFile, append: bool = False) -> BinaryIO:
        mode = "ab" if append else "wb"
        try:
            return open(file.path, mode)
        except (OSError, PermissionError) as e:
            raise FsException(f"Cannot write: {file.path} ({e})")

