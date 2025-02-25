from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
from os import makedirs
from os import remove
from os import walk
from os.path import exists
from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from typing import Iterator
from typing import Optional

from . import FileListMapping
from ....utils import File


def _get_key(path: str) -> str:
    return urlsafe_b64encode(path.encode()).rstrip(b"=").decode()


def _get_path(key: str) -> str:
    return urlsafe_b64decode(key.encode() + b"=" * (-len(key) % 8)).decode()


class LocalFileListMapping(FileListMapping):
    def __init__(self, path: Optional[str] = None):
        if path is None:
            path = mkdtemp()
        self._path = path
        makedirs(self._path, exist_ok=True)
        super().__init__()

    def __len__(self):
        return len(next(walk(self._path))[2])

    def __contains__(self, key: str) -> bool:
        return exists(join(self._path, _get_key(key)))

    def __iter__(self) -> Iterator[str]:
        return map(_get_path, next(walk(self._path))[2])

    def __getitem__(self, key: str) -> File:
        try:
            with open(join(self._path, _get_key(key))) as file:
                return File.decode(key, file.read())
        except FileNotFoundError:
            raise KeyError(key)

    def __setitem__(self, key: str, value: File):
        with open(join(self._path, _get_key(key)), "w") as file:
            file.write(value.encode())

    def __delitem__(self, key: str):
        try:
            remove(join(self._path, _get_key(key)))
        except FileNotFoundError:
            raise KeyError(key)

    def clear(self):
        rmtree(self._path)
        makedirs(self._path, exist_ok=True)
