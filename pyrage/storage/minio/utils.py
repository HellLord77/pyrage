from hashlib import md5

from minio.helpers import MAX_PART_SIZE

from ...utils import Hash


class MinIOCompositeHash(Hash):
    def __init__(self, data: bytes = b""):
        self._hash = md5()
        self._part_count = 0
        self._part_size = 0
        self._part_hash = md5()
        self.update(data)

    @property
    def name(self) -> str:
        return "etag"

    @property
    def digest_size(self) -> int:
        return -1

    def hexdigest(self) -> str:
        if self._part_size:
            self._hash.update(self._part_hash.digest())
            self._part_count += 1
            self._part_size = 0
        return f"{self._hash.hexdigest()}-{self._part_count}"

    def update(self, data: bytes):
        while data:
            size = MAX_PART_SIZE - self._part_size
            part = data[:size]
            self._part_size += len(part)
            self._part_hash.update(part)
            if len(part) == size:
                self._hash.update(self._part_hash.digest())
                self._part_count += 1
                self._part_size = 0
                self._part_hash = md5()
            data = data[size:]
