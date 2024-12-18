from . import FileFilter
from ....utils import File


class PathPrefixFileFilter(FileFilter):
    def __init__(self, invert: bool = False, path_prefix: str = ""):
        self._path_prefix = path_prefix
        super().__init__(invert)

    def __call__(self, file: File) -> bool:
        return file.path.startswith(self._path_prefix)
