from re import Pattern
from re import compile

from ....utils import File
from . import FileFilter


class PathRegexFileFilter(FileFilter):
    def __init__(self, invert: bool = False, path_regex: Pattern = compile(".*")):
        self._path_regex = path_regex
        super().__init__(invert)

    def __call__(self, file: File) -> bool:
        return self._path_regex.match(file.path) is not None
