from csv import QUOTE_STRINGS
from csv import reader
from csv import writer
from itertools import starmap
from typing import Iterator

from . import StorageCache
from ....utils import File


class CSVStorageCache(StorageCache):
    EXTENSION = "csv"

    def _dump_file_list(self):
        with open(self._cache_path, "w", newline="") as cache:
            writer(cache, quoting=QUOTE_STRINGS).writerows(self)

    def _load_file_list(self) -> Iterator[File]:  # FIXME type(size) = float
        with open(self._cache_path, "r") as cache:
            return starmap(File, reader(cache, quoting=QUOTE_STRINGS))
