from ....utils import File
from . import FileTransformer


class PathPrefixFileTransformer(FileTransformer):
    def __init__(self, path_prefix: str):
        self._path_prefix = path_prefix
        self._prefix_len = len(path_prefix)

    def _apply(self, file: File) -> File:
        return file._replace(path=file.path[self._prefix_len :])

    def _revert(self, file: File) -> File:
        return file._replace(path=f"{self._path_prefix}{file.path}")
