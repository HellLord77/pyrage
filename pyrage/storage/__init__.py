from __future__ import annotations

import logging
from abc import ABCMeta
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from typing import Iterable
from typing import Iterator
from typing import Optional

from tqdm import tqdm

from pyrage.config import STORAGE_DRY_RUN
from pyrage.config import STORAGE_MAX_THREADS
from pyrage.utils import File
from pyrage.utils import Readable

logger = logging.getLogger(__name__)


class Storage(metaclass=ABCMeta):
    _file_list: dict[str, File]

    def __init__(self):
        self._file_list = {}

    def __repr__(self):
        return f"{type(self).__name__}({len(self._file_list)})"

    def _add_file_list(self, file: File):
        self._file_list[file.path] = file

    def get_file_list(self) -> dict[str, File]:
        logger.info("[#] %s", locals())
        return self._file_list

    def diff_file_list(self, other: Storage, strict: bool = True) -> Iterator[File]:
        for file in self._file_list.values():
            try:
                other_file = other._file_list[file.path]
            except KeyError:
                yield file
            else:
                if strict and file != other_file:
                    yield file

    @abstractmethod
    def _get_file(self, file: File) -> Readable:
        raise NotImplementedError

    def get_file(self, file: File) -> Optional[Readable]:
        logger.info("[g] %s", locals())
        if not STORAGE_DRY_RUN:
            return self._get_file(file)

    def get_file_data(self, file: File) -> Optional[bytes]:
        readable = self.get_file(file)
        if readable is not None:
            return readable.read()

    @abstractmethod
    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def set_file(self, file: File, readable: Readable):
        logger.info("[s] %s", locals())
        if not STORAGE_DRY_RUN:
            self._set_file(file, readable)

    @abstractmethod
    def _del_file(self, file: File):
        raise NotImplementedError

    def del_file(self, file: File):
        logger.info("[d] %s", locals())
        if not STORAGE_DRY_RUN:
            self._del_file(file)

    def _del_files(self, files: Iterable[File]):
        try:
            # noinspection PyTypeChecker
            total = len(files)
        except TypeError:
            total = None
        with (
            ThreadPoolExecutor(STORAGE_MAX_THREADS) as executor,
            tqdm(total=total) as progress,
        ):
            for _ in as_completed(
                executor.submit(self.del_file, file) for file in files
            ):
                progress.update(1)

    def del_files(self, files: Iterable[File]):
        logger.info("[D] %s", locals())
        if not STORAGE_DRY_RUN:
            self._del_files(files)

    def _copy_file(self, src: File | Storage, dst: File):
        if isinstance(src, Storage):
            src = src._get_file(dst)
        elif isinstance(src, File):
            src = self._get_file(src)
        self._set_file(dst, src)

    def copy_file(self, src: File | Storage, dst: File):
        logger.info("[c] %s", locals())
        if not STORAGE_DRY_RUN:
            self._copy_file(src, dst)

    def _copy_files(self, src: Storage, dsts: Iterable[File]):
        try:
            # noinspection PyTypeChecker
            total = len(dsts)
        except TypeError:
            total = None
        with (
            ThreadPoolExecutor(STORAGE_MAX_THREADS) as executor,
            tqdm(total=total) as progress,
        ):
            for _ in as_completed(
                executor.submit(self._copy_file, src, dst) for dst in dsts
            ):
                progress.update(1)

    def copy_files(self, src: Storage, dsts: Iterable[File]):
        logger.info("[C] %s", locals())
        if not STORAGE_DRY_RUN:
            self._copy_files(src, dsts)

    def _move_file(self, src: File, dst: File | Storage):
        if isinstance(dst, Storage):
            dst = dst._get_file(src)
        self._copy_file(src, dst)
        self._del_file(src)

    def move_file(self, src: File, dst: File | Storage):
        logger.info("[m] %s", locals())
        if not STORAGE_DRY_RUN:
            self._move_file(src, dst)

    def sync(self, other: Storage):
        with ThreadPoolExecutor() as executor:
            for future in as_completed(
                (
                    executor.submit(other.get_file_list),
                    executor.submit(self.get_file_list),
                )
            ):
                future.result()
        self.copy_files(other, tuple(other.diff_file_list(self)))
        self.del_files(tuple(self.diff_file_list(other, False)))
