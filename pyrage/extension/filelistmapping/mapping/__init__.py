from abc import ABCMeta
from typing import MutableMapping

from ....utils import File


class FileListMapping(MutableMapping[str, File], metaclass=ABCMeta):
    _file_list: MutableMapping[str, File]

    def __del__(self):
        self.clear()
