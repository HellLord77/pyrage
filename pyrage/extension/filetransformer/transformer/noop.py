from . import FileTransformer

from ....utils import File


class NoopFileTransformer(FileTransformer):
    def _apply(self, file: File) -> File:
        return file

    def _revert(self, file: File) -> File:
        return file
