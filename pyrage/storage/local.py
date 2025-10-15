from hashlib import md5, sha1, sha256
from pathlib import Path
from shutil import copyfileobj
from tempfile import mkdtemp
from typing import Iterable

from ..config import LOCAL_EXTEND_GENERATE
from ..utils import CRC32Hash, File, Readable, WritableHash, WritableTee
from . import Storage


def _get_hash(path: Path) -> dict[str, str]:
    crc32 = WritableHash(CRC32Hash())
    md5_ = WritableHash(md5())
    sha1_ = WritableHash(sha1())
    sha256_ = WritableHash(sha256())
    writable = WritableTee(crc32, md5_, sha1_, sha256_)
    with path.open("rb") as file:
        copyfileobj(file, writable)
    return {
        "crc32": crc32.hexdigest(),
        "md5": md5_.hexdigest(),
        "sha1": sha1_.hexdigest(),
        "sha256": sha256_.hexdigest(),
    }


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
                    **_get_hash(path) if LOCAL_EXTEND_GENERATE else {},
                )

    def _get_file(self, file: File) -> Readable:
        return (self._path / file.path).open("rb")

    def _set_file(self, file: File, readable: Readable):
        path = self._path / file.path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as file:
            copyfileobj(readable, file)

    def _del_file(self, file: File):
        (self._path / file.path).unlink()


class TemporaryLocalStorage(LocalStorage):
    def __init__(self):
        super().__init__(mkdtemp())
