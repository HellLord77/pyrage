from hashlib import md5
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory

from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable
from pyrage.utils import WritableHash


def _get_md5(path: Path) -> str:
    md5_ = md5()
    writable = WritableHash(md5_)
    with path.open("rb") as file:
        copyfileobj(file, writable)
    return md5_.hexdigest()


class LocalStorage(Storage):
    def __init__(self, path: str):
        self._path = Path(path).resolve(strict=True)
        super().__init__()

    def _update_file_list(self):
        for path in self._path.rglob("*"):
            if path.is_file():
                self._add_file_list(
                    File(
                        path.relative_to(self._path).as_posix(),
                        **File.stat(path.stat()),
                        md5=_get_md5(path)
                    )
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
        self._temp = TemporaryDirectory()
        super().__init__(self._temp.name)
