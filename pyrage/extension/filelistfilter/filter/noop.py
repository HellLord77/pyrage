from . import FileListFilter
from ....utils import File


class NoopFileListFilter(FileListFilter):
    def __call__(self, file: File) -> bool:
        return True
