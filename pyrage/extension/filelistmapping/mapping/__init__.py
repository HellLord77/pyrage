from abc import ABCMeta
from typing import MutableMapping

from ....utils import File


class FileListMapping(MutableMapping[str, File], metaclass=ABCMeta):
    def __init__(self):
        self.clear()

    def __del__(self):
        self.clear()
