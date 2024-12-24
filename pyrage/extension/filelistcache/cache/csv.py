from csv import QUOTE_STRINGS
from csv import reader
from csv import writer
from itertools import starmap
from typing import Iterator

from . import FileListCache
from ....utils import File


class CSVFileListCache(FileListCache):
    EXTENSION = "csv"

    def _dump(self, files: Iterator[File]):
        with open(self.path, "w", encoding="utf-8", newline="") as cache:
            writer(cache, quoting=QUOTE_STRINGS).writerows(files)

    def _load(self) -> Iterator[File]:  # FIXME type(size) = float
        with open(self.path, "r", encoding="utf-8") as cache:
            yield from starmap(File, reader(cache, quoting=QUOTE_STRINGS))
