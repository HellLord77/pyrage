from pickle import dump
from pickle import load
from typing import Iterator

from . import StorageCache
from ....utils import File


class PickleStorageCache(StorageCache):
    EXTENSION = "pickle"

    def _dump_file_list(self):
        with open(self._cache_path, "wb") as file:
            dump(tuple(self), file)

    def _load_file_list(self) -> Iterator[File]:
        with open(self._cache_path, "rb") as file:
            return load(file)
