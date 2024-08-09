from typing import Iterator
from typing import NamedTuple
from typing import Optional
from typing import Protocol
from zlib import crc32

from requests import Response


class Hash(Protocol):
    def digest(self) -> bytes:
        pass

    def hexdigest(self) -> str:
        pass

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

    def hexdigest(self) -> str:
        return self.digest().hex()

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

    def __eq__(self, other):
        if isinstance(other, File):
            for field in ("size", "crc32", "md5"):
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

    @staticmethod
    def get_stat(stat: Stat) -> dict[str, Optional[int | float]]:
        # noinspection PyUnresolvedReferences
        return {
            field.removeprefix("st_"): getattr(stat, field, None)
            for field in Stat.__protocol_attrs__
        }
