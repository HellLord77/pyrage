from abc import ABCMeta
from types import MappingProxyType

from ...storage import Storage
from .mapping import FileListMapping


class StorageMapping(Storage, metaclass=ABCMeta):
    _t_file_list_mapping: type[FileListMapping]

    def __init__(self, *args, mapping_path: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_list = self._t_file_list_mapping(mapping_path)
        self._file_list_proxy = MappingProxyType(self._file_list)
