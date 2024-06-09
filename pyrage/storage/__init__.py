from __future__ import annotations

import functools
import logging
from abc import ABCMeta
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Optional

from tqdm.contrib.concurrent import thread_map

from pyrage.config import STORAGE_DRY_RUN
from pyrage.config import STORAGE_MAX_THREADS
from pyrage.utils import File
from pyrage.utils import Readable

logger = logging.getLogger(__name__)


class Storage(metaclass=ABCMeta):
    def __init__(self):
        self._file_list = {}
        self._file_list_proxy = MappingProxyType(self._file_list)

    def __repr__(self):
        return f"{type(self).__name__}({len(self._file_list)})"

    def _add_file_list(self, file: File):
        # logger.notset("[+] %s", file)
        self._file_list[file.path] = file

    @abstractmethod
    def _update_file_list(self):
        raise NotImplementedError

    def get_file_list(self) -> MappingProxyType[str, File]:
        if not self._file_list:
            self._update_file_list()
            logger.info("[#] %s", self)
        return self._file_list_proxy

    def sub_file_list(self, other: Storage, strict: bool = True) -> Iterator[File]:
        other_file_list = other.get_file_list()
        for file in self.get_file_list().values():
            try:
                other_file = other_file_list[file.path]
            except KeyError:
                yield file
            else:
                if strict and file != other_file:
                    yield file

    @abstractmethod
    def _get_file(self, file: File) -> Readable:
        raise NotImplementedError

    def get_file(self, file: File) -> Optional[Readable]:
        return _run(functools.partial(self._get_file, file))

    def get_file_data(self, file: File) -> Optional[bytes]:
        readable = self.get_file(file)
        if readable is not None:
            return readable.read()

    @abstractmethod
    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def set_file(self, file: File, readable: Readable):
        _run(functools.partial(self._set_file, file, readable))

    @abstractmethod
    def _del_file(self, file: File):
        raise NotImplementedError

    def del_file(self, file: File):
        _run(functools.partial(self._del_file, file))

    def _del_files(self, files: Storage | Iterable[File]):
        _execute(self._del_file, files)

    def del_files(self, files: Storage | Iterable[File]):
        _run(functools.partial(self._del_files, files))

    def _copy_file(self, src: File | Storage, dst: File):
        if isinstance(src, Storage):
            src = src._get_file(dst)
        elif isinstance(src, File):
            src = self._get_file(src)
        self._set_file(dst, src)

    def copy_file(self, src: File | Storage, dst: File):
        _run(functools.partial(self._copy_file, src, dst))

    def _copy_files(self, src: Storage, dsts: Storage | Iterable[File]):
        _execute(functools.partial(self._copy_file, src), dsts)

    def copy_files(self, src: Storage, dsts: Storage | Iterable[File]):
        _run(functools.partial(self._copy_files, src, dsts))

    def _move_file(self, src: File, dst: File | Storage):
        if isinstance(dst, Storage):
            dst = dst._get_file(src)
        self._copy_file(src, dst)
        self._del_file(src)

    def move_file(self, src: File, dst: File | Storage):
        _run(functools.partial(self._move_file, src, dst))

    def _move_files(self, srcs: Storage | Iterable[File], dst: Storage):
        _execute(functools.partial(self._move_file, dst=dst), srcs)

    def move_files(self, srcs: Storage | Iterable[File], dst: Storage):
        _run(functools.partial(self._move_files, srcs, dst))

    def clear(self):
        self.del_files(self)

    def sync(self, other: Storage):
        with ThreadPoolExecutor() as executor:
            for future in as_completed(
                (
                    executor.submit(self.get_file_list),
                    executor.submit(other.get_file_list),
                )
            ):
                future.result()
        self.copy_files(other, tuple(other.sub_file_list(self)))
        self.del_files(tuple(self.sub_file_list(other, False)))


def _run(partial: functools.partial) -> Any:
    name = partial.func.__name__
    n = name[1]
    if name.endswith("s"):
        n = n.upper()
    logger.info("[%s] %s", n, partial.args)
    if not STORAGE_DRY_RUN:
        return partial()


def _execute(func: Callable[[File], Any], files: Storage | Iterable[File]):
    if isinstance(files, Storage):
        files = files.get_file_list().values()
    thread_map(func, files, max_workers=STORAGE_MAX_THREADS)
