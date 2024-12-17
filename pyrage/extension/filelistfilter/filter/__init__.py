from abc import ABCMeta
from abc import abstractmethod
from itertools import filterfalse
from typing import Iterable

from ....utils import File


class FileListFilter(metaclass=ABCMeta):
    def __init__(self, invert: bool = False):
        self._filter = filterfalse if invert else filter

    @abstractmethod
    def __call__(self, file: File) -> bool:
        raise NotImplementedError

    def filter(self, files: Iterable[File]) -> Iterable[File]:
        return self._filter(self, files)
