from os.path import splitext

from . import FileFilter
from ....utils import File


class ExtensionFileFilter(FileFilter):
    def __init__(self, invert: bool = False, extension: str = ""):
        self._extension = extension
        super().__init__(invert)

    def __call__(self, file: File) -> bool:
        return splitext(file.path)[1] == self._extension
