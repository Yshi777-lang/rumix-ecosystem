"""
fs_tar.py — TAR как виртуальная ФС (чтение).
Порт идеи из Twig (fs-archive/TarFileSystem.kt), упрощён под Python tarfile.

Tar без центрального каталога: листинг — обход заголовков.
Python tarfile делает это сам; поддерживает gz/bz2/xz через режим 'r:*'.
"""

import tarfile
from pathlib import Path
from typing import BinaryIO, List, Optional

from .filesystem import FileSystem
from .xfile import XFile
from .fs_exception import FsException


SCHEME = "tar"

TAR_EXTENSIONS = {"tar", "tgz", "txz", "tbz", "tbz2"}


def is_tar_archive(file: XFile) -> bool:
    return (not file.is_dir) and (file.extension in TAR_EXTENSIONS)


class TarFileSystem(FileSystem):
    """TAR как виртуальная ФС. Только чтение."""

    def __init__(self, host_path: str, display_name: Optional[str] = None):
        self._host_path = str(Path(host_path).resolve())
        if not Path(self._host_path).exists():
            raise FsException(f"Archive not found: {self._host_path}")
        self._display_name = display_name or Path(self._host_path).name
        self._tar: Optional[tarfile.TarFile] = None
        self._members: Optional[List[tarfile.TarInfo]] = None

    @property
    def scheme(self) -> str:
        return SCHEME

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def host_path(self) -> str:
        return self._host_path

    def _open(self) -> tarfile.TarFile:
        if self._tar is None:
            try:
                self._tar = tarfile.open(self._host_path, "r:*")
            except (tarfile.TarError, OSError) as e:
                raise FsException(f"Cannot open tar: {self._host_path} ({e})")
        return self._tar

    def _members_list(self) -> List[tarfile.TarInfo]:
        if self._members is None:
            self._members = self._open().getmembers()
        return self._members

    def _to_xfile(self, inner_path: str) -> XFile:
        lookup = inner_path.lstrip("/")
        if lookup == "":
            return XFile(scheme=SCHEME, path="/", is_dir=True, can_read=True, can_write=False)
        tar = self._open()
        try:
            info = tar.getmember(lookup)
        except KeyError:
            prefix = lookup.rstrip("/") + "/"
            if any(m.name.startswith(prefix) for m in self._members_list()):
                return XFile(scheme=SCHEME, path=inner_path, is_dir=True, can_read=True, can_write=False)
            raise FsException(f"No such entry in tar: {inner_path}")
        return XFile(
            scheme=SCHEME,
            path="/" + info.name.rstrip("/"),
            is_dir=info.isdir(),
            size=info.size if not info.isdir() else 0,
            last_modified=float(info.mtime or 0),
            can_read=True,
            can_write=False,
        )

    def root(self) -> XFile:
        return XFile(scheme=SCHEME, path="/", is_dir=True, can_read=True, can_write=False)

    def resolve(self, path: str) -> XFile:
        return self._to_xfile(path)

    def stat(self, path: str) -> Optional[XFile]:
        try:
            return self._to_xfile(path)
        except FsException:
            return None

    def list(self, directory: XFile) -> List[XFile]:
        if not directory.is_dir:
            raise FsException(f"Not a directory in tar: {directory.path}")
        base = directory.path.rstrip("/")
        base_prefix = "" if base in ("", "/") else base.lstrip("/") + "/"
        seen = {}
        for m in self._members_list():
            if not m.name.startswith(base_prefix):
                continue
            rest = m.name[len(base_prefix):]
            if not rest:
                continue
            head = rest.split("/", 1)[0]
            is_dir = m.isdir() or ("/" in rest)
            full = (base_prefix + head).rstrip("/")
            full_path = "/" + full.lstrip("/")
            if full_path in seen:
                continue
            if is_dir:
                seen[full_path] = XFile(scheme=SCHEME, path=full_path, is_dir=True,
                                        can_read=True, can_write=False)
            else:
                seen[full_path] = XFile(scheme=SCHEME, path=full_path, is_dir=False,
                                        size=m.size, last_modified=float(m.mtime or 0),
                                        can_read=True, can_write=False)
        items = list(seen.values())
        return sorted(items, key=lambda f: (not f.is_dir, f.name.lower()))

    def open_input(self, file: XFile) -> BinaryIO:
        if file.is_dir:
            raise FsException(f"Is a directory: {file.path}")
        tar = self._open()
        try:
            member = tar.getmember(file.path.lstrip("/"))
            return tar.extractfile(member)
        except (KeyError, tarfile.TarError) as e:
            raise FsException(f"Cannot read from tar: {file.path} ({e})")

    def open_output(self, file: XFile, append: bool = False) -> BinaryIO:
        raise FsException("Writing to tar is not implemented yet (read-only).")

    def close(self) -> None:
        if self._tar is not None:
            self._tar.close()
            self._tar = None
            self._members = None
