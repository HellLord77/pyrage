from hashlib import md5
from typing import Iterable
from typing import Optional
from urllib.parse import urlparse

from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import InvalidResponseError
from minio.helpers import MAX_PART_SIZE

from . import Storage
from ..config import MINIO_RETRY_GENERATE
from ..utils import File
from ..utils import Hash
from ..utils import Readable


class _MinIOCompositeHash(Hash):
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


class MinIOStorage(Storage):
    def __init__(
        self,
        endpoint: str,
        bucket: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        parts = urlparse(endpoint)
        self._minio = Minio(
            parts.netloc, access_key, secret_key, secure="https" == parts.scheme
        )
        self._bucket = bucket
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        start_after = None
        object_ = None
        while True:
            try:
                for object_ in self._minio.list_objects(
                    self._bucket, recursive=True, start_after=start_after
                ):
                    yield File(
                        object_.object_name,
                        size=object_.size,
                        mtime=object_.last_modified.timestamp(),
                        md5=object_.etag if len(object_.etag) == 32 else None,
                    )
            except InvalidResponseError:
                if MINIO_RETRY_GENERATE:
                    if object_ is not None:
                        start_after = object_.object_name
                else:
                    raise
            else:
                break

    def __generate_file_list(self) -> Iterable[File]:
        prefixes = [""]
        while prefixes:
            for object_ in self._minio.list_objects(
                self._bucket, prefix=prefixes.pop(0)
            ):
                if object_.is_dir:
                    prefixes.append(object_.object_name)
                else:
                    yield File(object_.object_name, size=object_.size, md5=object_.etag)

    def _get_file(self, file: File) -> Readable:
        return self._minio.get_object(self._bucket, file.path)

    def _set_file(self, file: File, readable: Readable):
        # noinspection PyTypeChecker
        self._minio.put_object(
            self._bucket, file.path, readable, -1, part_size=MAX_PART_SIZE
        )

    def _del_file(self, file: File):
        self._minio.remove_object(self._bucket, file.path)

    def __del_files(self, files: Iterable[File]):
        for error in self._minio.remove_objects(
            self._bucket, (DeleteObject(file.path) for file in files)
        ):
            raise error
