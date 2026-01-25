from ....utils import File
from . import FileTransformer


class PathStreamFileTransformer(FileTransformer):
    def __init__(self):
        self._transform = {}

    def _apply(self, file: File) -> File:
        path, stream = file.path.rsplit(":", 1)
        self._transform[path] = stream
        return file._replace(path=path)

    def _revert(self, file: File) -> File:
        return file._replace(path=f"{file.path}:{self._transform[file.path]}")
