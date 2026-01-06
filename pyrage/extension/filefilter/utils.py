from abc import ABCMeta
from collections.abc import Iterable
from collections.abc import Mapping

from ...storage import Storage
from ...utils import File
from .filter import FileFilter


class StorageFilter(Storage, metaclass=ABCMeta):
    _t_file_filter: type[FileFilter]

    # noinspection PyDefaultArgument
    def __init__(
        self,
        *args,
        filter_invert: bool | None = None,
        filter_args: Iterable = (),
        filter_kwargs: Mapping = {},
        **kwargs,
    ):
        if filter_invert is None:
            filter_invert = False
        self._file_filter = self._t_file_filter(filter_invert, *filter_args, **filter_kwargs)
        super().__init__(*args, **kwargs)

    def _generate_file_list(self) -> Iterable[File]:
        return self._file_filter.filter(super()._generate_file_list())
