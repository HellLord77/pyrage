from __future__ import annotations

import logging
from abc import ABCMeta
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from functools import cache
from functools import partial
from io import BytesIO
from itertools import chain
from itertools import islice
from types import MappingProxyType
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import MutableMapping
from typing import Optional
from warnings import deprecated

from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map
from tqdm.utils import CallbackIOWrapper

from ..config import STORAGE_DRY_RUN
from ..config import STORAGE_MAX_THREADS
from ..utils import File
from ..utils import Readable
from ..utils import consume

logger = logging.getLogger(__name__)


class Storage(metaclass=ABCMeta):
    _file_list: MutableMapping[str, File]

    _fetch_file_list_init: bool = False

    def __init__(self, *_, **__):
        self._file_list = {}
        self._file_list_proxy = MappingProxyType(self._file_list)

    def __repr__(self):
        return f"{type(self).__name__}({len(self)})"

    def __len__(self):
        return self.len_file_list()

    def __iter__(self) -> Iterator[File]:
        return iter(self.fetch_file_list().values())

    def len_file_list(self) -> int:
        return len(self._file_list)

    def add_file_list(self, file: File):
        self._file_list[file.path] = file

    @abstractmethod
    def _generate_file_list(self) -> Iterable[File]:
        raise NotImplementedError

    def _fetch_file_list(self):
        consume(map(self.add_file_list, self._generate_file_list()))
        logger.info("[#] %s", self)

    def fetch_file_list(self) -> MappingProxyType[str, File]:
        if not self._fetch_file_list_init:
            self._fetch_file_list_init = True
            self._fetch_file_list()
        return self._file_list_proxy

    def rev_diff_file_list(
        self, files: Iterable[File], *, strict: bool = True
    ) -> Iterator[File]:
        file_list = self.fetch_file_list()
        for file in files:
            try:
                self_file = file_list[file.path]
            except KeyError:
                yield file
            else:
                if strict and file != self_file:
                    yield file

    @deprecated("")
    def union(self, files: Iterable[File], *, strict: bool = True) -> Iterator[File]:
        yield from self
        self_files = self.fetch_file_list()
        for file in files:
            try:
                self_file = self_files[file.path]
            except KeyError:
                yield file
            else:
                if strict and file != self_file:
                    yield file

    @deprecated("")
    def intersection(
        self, files: Iterable[File], *, strict: bool = True
    ) -> Iterator[File]:
        if isinstance(files, Storage):
            files = files.fetch_file_list()
        else:
            files = {file.path: file for file in files}
        for file in self:
            try:
                other_file = files[file.path]
            except KeyError:
                continue
            else:
                if not strict or file == other_file:
                    yield file

    @deprecated("")
    def difference(
        self, files: Iterable[File], *, strict: bool = True
    ) -> Iterator[File]:
        if isinstance(files, Storage):
            files = files.fetch_file_list()
        else:
            files = {file.path: file for file in files}
        for file in self:
            try:
                other_file = files[file.path]
            except KeyError:
                yield file
            else:
                if strict and file != other_file:
                    yield file

    @abstractmethod
    def _get_file(self, file: File) -> Readable:
        raise NotImplementedError

    def get_file(self, file: File) -> Optional[Readable]:
        return _run(partial(self._get_file, file))

    def get_file_data(self, file: File) -> Optional[bytes]:
        readable = self.get_file(file)
        if readable is not None:
            return readable.read()

    @abstractmethod
    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def set_file(self, file: File, readable: Readable):
        _run(partial(self._set_file, file, readable))

    def set_file_data(self, file: File, data: bytes):
        self.set_file(file, BytesIO(data))

    @abstractmethod
    def _del_file(self, file: File):
        raise NotImplementedError

    def del_file(self, file: File):
        _run(partial(self._del_file, file))

    def _del_files(self, files: Iterable[File]):
        _execute(self._del_file, files)

    def del_files(self, files: Iterable[File]):
        _run(partial(self._del_files, files))

    def _copy_file(self, src: File | Storage, dst: File):
        if isinstance(src, Storage):
            total = dst.size
            src = src._get_file(dst)
        else:
            total = src.size
            src = self._get_file(src)
        with tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            dynamic_ncols=True,
            unit_divisor=1024,
        ) as t:
            self._set_file(dst, CallbackIOWrapper(t.update, src))

    def copy_file(self, src: File | Storage, dst: File):
        _run(partial(self._copy_file, src, dst))

    def _copy_files(self, src: Storage, dsts: Iterable[File]):
        _execute(partial(self._copy_file, src), dsts)

    def copy_files(self, src: Storage, dsts: Iterable[File]):
        _run(partial(self._copy_files, src, dsts))

    def _move_file(self, src: File, dst: File | Storage):
        if isinstance(dst, Storage):
            dst = dst._get_file(src)
        self._copy_file(src, dst)
        self._del_file(src)

    def move_file(self, src: File, dst: File | Storage):
        _run(partial(self._move_file, src, dst))

    def _move_files(self, srcs: Iterable[File], dst: Storage):
        _execute(partial(self._move_file, dst=dst), srcs)

    def move_files(self, srcs: Iterable[File], dst: Storage):
        _run(partial(self._move_files, srcs, dst))

    def clear(self):
        self.fetch_file_list()
        self.del_files(self)

    def sync(self, *others: Storage):
        with ThreadPoolExecutor() as executor:
            futures = chain(
                (executor.submit(self.fetch_file_list),),
                (executor.submit(other.fetch_file_list) for other in others),
            )
            for future in as_completed(futures):
                future.result()
        for index, other in enumerate(others):
            copy_files = other
            for rest in islice(others, index + 1, None):
                copy_files = rest.rev_diff_file_list(copy_files)
            self.copy_files(other, tuple(self.rev_diff_file_list(copy_files)))
        del_files = self
        for other in others:
            del_files = other.rev_diff_file_list(del_files, strict=False)
        self.del_files(tuple(del_files))


@cache
def _name(func: Callable) -> str:
    name = func.__name__
    n = name[1]
    if name.endswith("s"):
        n = n.upper()
    return n


def _run(func: partial) -> Any:
    # noinspection PyTypeChecker
    logger.info("[%s] %s", _name(func.func), func.args)
    if not STORAGE_DRY_RUN:
        return func()


def _execute(func: Callable[[File], Any], files: Iterable[File]):
    thread_map(
        func,
        files,
        max_workers=STORAGE_MAX_THREADS,
        unit="file",
        dynamic_ncols=True,
    )
