from __future__ import annotations

from collections import deque
from itertools import islice
from os import SEEK_CUR
from os import SEEK_END
from os import SEEK_SET
from re import compile
from shutil import COPY_BUFSIZE
from tempfile import TemporaryFile
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import NamedTuple
from posixpath import sep
from typing import Optional
from typing import Protocol
from typing import TypeVar
from zlib import crc32

from requests import Response
from requests import Session

T = TypeVar("T")


class Hash(Protocol):
    def digest(self) -> bytes:
        return bytes.fromhex(self.hexdigest())

    def hexdigest(self) -> str:
        return self.digest().hex()

    def update(self, data: bytes):
        pass


class CRC32Hash(Hash):
    def __init__(self, data: bytes = b"", *, value: Optional[int] = None):
        if value is None:
            value = crc32(data)
        self._hash = value

    @property
    def name(self) -> str:
        return "crc32"

    @property
    def digest_size(self) -> int:
        return 4

    def digest(self) -> bytes:
        return self._hash.to_bytes(self.digest_size, "big")

    def update(self, data: bytes):
        self._hash = crc32(data, self._hash)


class Readable(Protocol):
    @staticmethod
    def readable() -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        pass


class ReadableIterator(Readable):
    def __init__(self, iterator: Iterator[bytes]):
        self._buffer = b""
        self._iterator = iterator

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = None
        length = len(self._buffer)
        while (size is None or length < size) and (
            buffer := next(self._iterator, None) is not None
        ):
            self._buffer += buffer
            length += len(buffer)
        data, self._buffer = self._buffer[:size], self._buffer[size:]
        return data


class ReadableResponse(Readable):
    def __init__(self, response: Response):
        response.raise_for_status()
        self._raw = response.raw
        self._raw.decode_content = True

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = None
        return self._raw.read(size)


class Seekable(Protocol):
    @staticmethod
    def seekable() -> bool:
        return True

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        pass

    def tell(self) -> int:
        return self.seek(0, SEEK_CUR)

    def truncate(self, size: Optional[int] = None) -> int:
        raise NotImplementedError


class ReadableSeekable(Readable, Seekable, Protocol):
    pass


class SeekableReadable(ReadableSeekable):
    def __init__(self, readable: Readable):
        self._position = 0
        self._buffer = TemporaryFile()
        self._readable = readable

    def _fill(self, position: Optional[int] = None) -> int:
        self._buffer.seek(0, SEEK_END)
        length = self._buffer.tell()
        while (position is None or length < position) and (
            buffer := self._readable.read(COPY_BUFSIZE)
        ):
            self._buffer.write(buffer)
            length += len(buffer)
        return length

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = None
        self._fill(None if size is None else self._position + size)
        self._buffer.seek(self._position)
        data = self._buffer.read(size)
        self._position += len(data)
        return data

    def seek(self, offset: int, whence: int = SEEK_SET) -> int:
        if whence == SEEK_SET:
            self._position = offset
        elif whence == SEEK_CUR:
            self._position = self._position + offset
        elif whence == SEEK_END:
            self._position = self._fill() + offset
        else:
            raise NotImplementedError
        self._fill(self._position)
        return self._position

    def tell(self) -> int:
        return self._position


class Writable(Protocol):
    @staticmethod
    def writable() -> bool:
        return True

    def write(self, data: bytes):
        pass

    def truncate(self, size: Optional[int] = None) -> int:
        raise NotImplementedError


class WritableTee(Writable):
    def __init__(self, *writables: Writable):
        self._writables = writables

    def write(self, data: bytes):
        for writable in self._writables:
            writable.write(data)


class WritableHash(Protocol):
    # noinspection PyShadowingBuiltins
    def __init__(self, hash: Hash):
        self.digest = hash.digest
        self.hexdigest = hash.hexdigest
        self.write = hash.update


class DefragmentedSession(Session):
    def request(self, method: str, url: str, *args, **kwargs) -> Response:
        return super().request(method, url.replace("#", "%23"), *args, **kwargs)


class Stat(Protocol):
    def st_size(self) -> int:
        pass

    def st_mtime(self) -> float:
        pass

    def st_atime(self) -> float:
        pass

    def st_ctime(self) -> float:
        pass


class File(NamedTuple):
    path: str
    size: Optional[int] = None
    mtime: Optional[float] = None
    atime: Optional[float] = None
    ctime: Optional[float] = None
    crc32: Optional[str] = None
    md5: Optional[str] = None
    sha1: Optional[str] = None
    sha256: Optional[str] = None

    _PAT_FLOAT = compile(r"\d+\.\d+")

    def __eq__(self, other):
        if isinstance(other, File):
            for field in ("size", "crc32", "md5", "sha1", "sha256"):
                # noinspection PyUnboundLocalVariable
                if (
                    (value := getattr(self, field)) is not None
                    and (other_value := getattr(other, field)) is not None
                    and value != other_value
                ):
                    return False
            return True
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def encode(self) -> str:
        return ",".join(
            "" if value is None else str(value) for value in islice(self, 1, None)
        )

    @classmethod
    def decode(cls, path: str, values: str) -> File:
        return cls(path, *map(cls._decode_value, values.split(",")))

    @classmethod
    def _decode_value(cls, value: str) -> Optional[int | float | str]:
        if value == "":
            value = None
        elif value.isdigit():
            value = int(value)
        elif cls._PAT_FLOAT.fullmatch(value):
            value = float(value)
        return value

    @staticmethod
    def get_stat(stat: Stat) -> dict[str, Optional[int | float]]:
        # noinspection PyUnresolvedReferences
        return {
            field.removeprefix("st_"): getattr(stat, field, None)
            for field in Stat.__protocol_attrs__
        }


def is_seekable(obj: Any) -> bool:
    seekable = getattr(obj, "seekable", None)
    if isinstance(seekable, Callable):
        seekable = seekable()
    if not isinstance(seekable, bool):
        seekable = False
    return seekable


def iter_join(separator: T, iterable: Iterable[T]) -> Iterable[T]:
    iterator = iter(iterable)
    try:
        yield next(iterator)
    except StopIteration:
        return
    for item in iterator:
        yield separator
        yield item


def consume(iterator, n: Optional[int] = None):
    if n is None:
        deque(iterator, maxlen=0)
    else:
        next(islice(iterator, n, n), None)

def lsplit(path: str) -> tuple[str, str]:
    index = path.find(sep)
    if index < 0:
        return "", path
    else:
        return path[:index], path[index + 1 :]
