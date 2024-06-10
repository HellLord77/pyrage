from itertools import starmap
from json import dump
from json import load
from typing import Iterable
from typing import Iterator
from typing import TextIO

from . import StorageCache
from ....utils import File


class JSONStorageCache(StorageCache):
    EXTENSION = "json"

    @staticmethod
    def _dump_file_list(writable: TextIO, files: Iterable[File]):
        dump(tuple(files), writable, separators=(",", ":"))

    @staticmethod
    def _load_file_list(readable: TextIO) -> Iterator[File]:
        return starmap(File, load(readable))
