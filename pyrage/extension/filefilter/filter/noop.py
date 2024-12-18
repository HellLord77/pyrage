from . import FileFilter
from ....utils import File


class NoopFileFilter(FileFilter):
    def __call__(self, file: File) -> bool:
        return True
