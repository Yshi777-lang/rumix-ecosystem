"""
fs_zip.py — ZIP-архив как файловая система (чтение).
Порт идеи из Twig (fs-archive/ZipFileSystem.kt), упрощён под Python zipfile.

Архив монтируется как виртуальное дерево:
  scheme='zip', path='/inner/путь/в/архиве', плюс host-путь к самому .zip.
"""

import zipfile
from pathlib import Path
from typing import BinaryIO, List, Optional

from .filesystem import FileSystem
from .xfile import XFile
from .fs_exception import FsException


SCHEME = "zip"

# расширения, которые считаем zip-архивами
ZIP_EXTENSIONS = {"zip", "jar", "apk", "xapk", "apks", "apkm"}


def is_zip_archive(file: XFile) -> bool:
    """По расширению: является ли запись zip-архивом."""
    return (not file.is_dir) and (file.extension in ZIP_EXTENSIONS)


class ZipFileSystem(FileSystem):
    """
    ZIP как виртуальная ФС.
    path внутри архива: '/dir/file.txt'; корень — '/'.
    host_path — путь к самому .zip на локальном диске.
    """

    def __init__(self, host_path: str, display_name: Optional[str] = None):
        self._host_path = str(Path(host_path).resolve())
        if not Path(self._host_path).exists():
            raise FsException(f"Archive not found: {self._host_path}")
        self._display_name = display_name or Path(self._host_path).name
        self._zip: Optional[zipfile.ZipFile] = None
        self._names: Optional[List[str]] = None

    @property
    def scheme(self) -> str:
        return SCHEME

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def host_path(self) -> str:
        return self._host_path

    def _open(self) -> zipfile.ZipFile:
        if self._zip is None:
            try:
                self._zip = zipfile.ZipFile(self._host_path, "r")
            except (zipfile.BadZipFile, OSError) as e:
                raise FsException(f"Cannot open archive: {self._host_path} ({e})")
        return self._zip

    def _names_list(self) -> List[str]:
        if self._names is None:
            zf = self._open()
            self._names = zf.namelist()
        return self._names

    def _to_xfile(self, inner_path: str) -> XFile:
        zf = self._open()
        # нормализуем: без ведущего слэша для zipfile
        lookup = inner_path.lstrip("/") if inner_path != "/" else ""
        if lookup == "" or lookup.endswith("/"):
            return XFile(
                scheme=SCHEME, path=inner_path, is_dir=True, size=0,
                last_modified=0.0, can_read=True, can_write=False,
            )
        try:
            info = zf.getinfo(lookup)
        except KeyError:
            # может быть директория без явной записи — проверяем префикс
            prefix = lookup.rstrip("/") + "/"
            if any(n.startswith(prefix) for n in self._names_list()):
                return XFile(
                    scheme=SCHEME, path=inner_path, is_dir=True, size=0,
                    last_modified=0.0, can_read=True, can_write=False,
                )
            raise FsException(f"No such entry in archive: {inner_path}")
        return XFile(
            scheme=SCHEME,
            path=inner_path,
            is_dir=info.is_dir(),
            size=info.file_size,
            last_modified=0.0,  # zip-тайм пока не парсим
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
            raise FsException(f"Not a directory in archive: {directory.path}")
        base = directory.path.rstrip("/")
        base_prefix = "" if base in ("", "/") else base.lstrip("/") + "/"
        seen = {}
        for name in self._names_list():
            if not name.startswith(base_prefix):
                continue
            rest = name[len(base_prefix):]
            if rest == "":
                continue
            head = rest.split("/", 1)[0]
            is_dir = ("/" in rest) or name.endswith("/")
            full = (base_prefix + head).rstrip("/")
            full_path = "/" + full.lstrip("/")
            if full_path in seen:
                continue
            if is_dir:
                seen[full_path] = XFile(scheme=SCHEME, path=full_path, is_dir=True,
                                        size=0, last_modified=0.0, can_read=True, can_write=False)
            else:
                try:
                    info = self._open().getinfo(name)
                    size = info.file_size
                except KeyError:
                    size = 0
                seen[full_path] = XFile(scheme=SCHEME, path=full_path, is_dir=False,
                                        size=size, last_modified=0.0, can_read=True, can_write=False)
        items = list(seen.values())
        return sorted(items, key=lambda f: (not f.is_dir, f.name.lower()))

    def open_input(self, file: XFile) -> BinaryIO:
        if file.is_dir:
            raise FsException(f"Is a directory: {file.path}")
        zf = self._open()
        try:
            return zf.open(file.path.lstrip("/"), "r")
        except (KeyError, zipfile.BadZipFile) as e:
            raise FsException(f"Cannot read from archive: {file.path} ({e})")

    def open_output(self, file: XFile, append: bool = False) -> BinaryIO:
        if file.is_dir:
            raise FsException(f"Is a directory: {file.path}")
        return ZipWriteBuffer(self, file.path, append=append)

    def close(self) -> None:
        if self._zip is not None:
            self._zip.close()
            self._zip = None
            self._names = None


class ZipWriteBuffer:
    """
    Буфер записи в ZIP. Копит байты в памяти,
    при close() добавляет запись в архив (перезаписывая .zip).
    """
    def __init__(self, fs: "ZipFileSystem", inner_path: str, append: bool = False):
        self._fs = fs
        self._inner_path = inner_path.lstrip("/")
        self._append = append
        self._buf = bytearray()

    def write(self, data: bytes) -> int:
        self._buf.extend(data)
        return len(data)

    def close(self) -> None:
        fs = self._fs
        fs._open()
        fs._zip.close()
        fs._zip = None
        fs._names = None
        # перезаписываем архив: старое содержимое + новая запись
        import zipfile as _zf
        from pathlib import Path as _P
        old_entries = {}
        try:
            with _zf.ZipFile(fs._host_path, "r") as z:
                for name in z.namelist():
                    old_entries[name] = z.read(name)
        except (FileNotFoundError, _zf.BadZipFile):
            pass
        if self._append and self._inner_path in old_entries:
            old_entries[self._inner_path] = old_entries[self._inner_path] + bytes(self._buf)
        else:
            old_entries[self._inner_path] = bytes(self._buf)
        with _zf.ZipFile(fs._host_path, "w", _zf.ZIP_DEFLATED) as z:
            for name, data in old_entries.items():
                z.writestr(name, data)
