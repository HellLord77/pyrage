from abc import ABCMeta
from typing import Iterable
from typing import Optional

from .filter import FileListFilter
from ...storage import Storage
from ...utils import File


class StorageFilter(Storage, metaclass=ABCMeta):
    _t_file_list_filter: type[FileListFilter]

    def __init__(self, *args, filter_invert: Optional[bool] = None, **kwargs):
        if filter_invert is None:
            filter_invert = False
        self._file_list_filter = self._t_file_list_filter(filter_invert)
        super().__init__(*args, **kwargs)

    def _generate_file_list(self) -> Iterable[File]:
        return self._file_list_filter.filter(super()._generate_file_list())
