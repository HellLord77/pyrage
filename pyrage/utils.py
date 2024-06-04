from dataclasses import KW_ONLY
from dataclasses import dataclass
from typing import Iterator
from typing import Optional
from typing import Protocol

from requests import Response


class Hash(Protocol):
    def update(self, data: bytes):
        pass


class Readable(Protocol):
    def read(self, size: int = -1) -> bytes:
        pass


class ReadableIterator(Readable):
    def __init__(self, iterator: Iterator[bytes]):
        self._buffer = b""
        self._iterator = iterator

    def read(self, size: int = -1) -> bytes:
        while size < 0 or len(self._buffer) < size:
            try:
                self._buffer += next(self._iterator)
            except StopIteration:
                break
        result, self._buffer = self._buffer[:size], self._buffer[size:]
        return result


class ReadableResponse(Readable):
    def __init__(self, response: Response):
        response.raise_for_status()
        self._raw = response.raw
        self._raw.decode_content = True

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = None
        return self._raw.read(size)


class Writable(Protocol):
    def write(self, data: bytes):
        pass


class WritableHash(Protocol):
    # noinspection PyShadowingBuiltins
    def __init__(self, hash: Hash):
        self.write = hash.update


@dataclass(frozen=True)
class File:
    path: str
    _: KW_ONLY
    size: Optional[int] = None
    mtime: Optional[float] = None
    atime: Optional[float] = None
    ctime: Optional[float] = None
    md5: Optional[str] = None

    def __eq__(self, other):
        if isinstance(other, File):
            for prop in ("size", "md5"):
                # noinspection PyUnboundLocalVariable
                if (
                    (self_prop := getattr(self, prop)) is not None
                    and (other_prop := getattr(other, prop)) is not None
                    and self_prop != other_prop
                ):
                    return False
            return True
        return NotImplemented
