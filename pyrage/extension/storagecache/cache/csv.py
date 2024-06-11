from csv import QUOTE_STRINGS
from csv import reader
from csv import writer
from itertools import starmap
from typing import Iterable
from typing import Iterator
from typing import TextIO

from . import StorageCache
from ....utils import File


class CSVStorageCache(StorageCache):
    EXTENSION = "csv"

    @staticmethod
    def _dump_file_list(writable: TextIO, files: Iterable[File]):
        writer(writable, quoting=QUOTE_STRINGS).writerows(files)

    @staticmethod
    def _load_file_list(readable: TextIO) -> Iterator[File]:  # FIXME type(size) = float
        return starmap(File, reader(readable, quoting=QUOTE_STRINGS))
