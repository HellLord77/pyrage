from . import FileTransformer

from ....utils import File


class PathPrefixFileTransformer(FileTransformer):
    def __init__(self, path_prefix: str):
        self._path_prefix = path_prefix

    def _apply(self, file: File) -> File:
        return file._replace(path=file.path.removeprefix(self._path_prefix))

    def _revert(self, file: File) -> File:
        return file._replace(path=self._path_prefix + file.path)
