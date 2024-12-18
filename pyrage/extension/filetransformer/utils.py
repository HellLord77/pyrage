from abc import ABCMeta
from typing import Iterable
from typing import Mapping

from .transformer import FileTransformer
from ...storage import Storage
from ...utils import File
from ...utils import Readable


class StorageTransformer(Storage, metaclass=ABCMeta):
    _t_file_transformer: type[FileTransformer]

    # noinspection PyDefaultArgument
    def __init__(
        self,
        *args,
        transformer_args: Iterable = (),
        transformer_kwargs: Mapping = {},
        **kwargs
    ):
        self._file_transformer = self._t_file_transformer(
            *transformer_args, **transformer_kwargs
        )
        super().__init__(*args, **kwargs)

    def _generate_file_list(self) -> Iterable[File]:
        return self._file_transformer.map(super()._generate_file_list())

    def _get_file(self, file: File) -> Readable:
        return super()._get_file(self._file_transformer.get(file))

    def _set_file(self, file: File, readable: Readable):
        super()._set_file(self._file_transformer.get(file), readable)

    def _del_file(self, file: File):
        super()._del_file(self._file_transformer.get(file))
