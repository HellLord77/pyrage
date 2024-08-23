from hashlib import md5
from pathlib import Path
from shutil import copyfileobj
from tempfile import mkdtemp
from typing import Iterable

from . import Storage
from ..utils import CRC32Hash
from ..utils import File
from ..utils import Readable
from ..utils import WritableHash
from ..utils import WritableTee


def _get_hash(path: Path) -> tuple[str, str]:
    crc32 = WritableHash(CRC32Hash())
    md5_ = WritableHash(md5())
    writable = WritableTee(crc32, md5_)
    with path.open("rb") as file:
        copyfileobj(file, writable)
    return crc32.hexdigest(), md5_.hexdigest()


class LocalStorage(Storage):
    def __init__(self, path: str):
        self._path = Path(path).resolve(strict=True)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for path in self._path.rglob("*"):
            if path.is_file():
                yield File(
                    path.relative_to(self._path).as_posix(),
                    **File.get_stat(path.stat()),
                    **dict(zip(("crc32", "md5"), _get_hash(path)))
                )

    def __generate_file_list(self) -> Iterable[File]:
        for path in self._path.rglob("*"):
            if path.is_file():
                yield File(
                    path.relative_to(self._path).as_posix(),
                    **File.get_stat(path.stat())
                )

    def _get_file(self, file: File) -> Readable:
        return open(self._path.joinpath(file.path), "rb")

    def _set_file(self, file: File, readable: Readable):
        path = self._path.joinpath(file.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as file:
            copyfileobj(readable, file)

    def _del_file(self, file: File):
        self._path.joinpath(file.path).unlink()


class TemporaryStorage(LocalStorage):
    def __init__(self):
        super().__init__(mkdtemp())
