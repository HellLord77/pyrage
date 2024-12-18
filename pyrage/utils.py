from __future__ import annotations

from itertools import islice
from re import compile
from typing import Iterator
from typing import NamedTuple
from typing import Optional
from typing import Protocol
from zlib import crc32

from requests import Response


class Hash(Protocol):
    def digest(self) -> bytes:
        return bytes.fromhex(self.hexdigest())

    def hexdigest(self) -> str:
        return self.digest().hex()

    def update(self, data: bytes):
        pass


class CRC32Hash(Hash):
    def __init__(self, data: bytes = b""):
        self._hash = crc32(data)

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

    _PAT_FLOAT = compile(r"\d+\.\d+")

    def __eq__(self, other):
        if isinstance(other, File):
            for field in ("size", "crc32", "md5", "sha1"):
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
