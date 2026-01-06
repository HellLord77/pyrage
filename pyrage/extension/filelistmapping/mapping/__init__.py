from abc import ABCMeta
from collections.abc import MutableMapping

from ....utils import File


class FileListMapping(MutableMapping[str, File], metaclass=ABCMeta):
    def __init__(self, _: str | None = None):
        self.clear()

    def __del__(self):
        self.clear()
