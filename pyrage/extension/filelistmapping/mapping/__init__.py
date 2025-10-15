from abc import ABCMeta
from typing import MutableMapping, Optional

from ....utils import File


class FileListMapping(MutableMapping[str, File], metaclass=ABCMeta):
    def __init__(self, _: Optional[str] = None):
        self.clear()

    def __del__(self):
        self.clear()
