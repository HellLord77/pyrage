from typing import Iterable
from urllib.parse import urlparse

from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import InvalidResponseError
from minio.helpers import MAX_PART_SIZE

# noinspection PyProtectedMember
from urllib3._collections import RecentlyUsedContainer

from . import Storage
from ..config import MINIO_RETRY_GENERATE
from ..config import STORAGE_MAX_THREADS
from ..utils import File
from ..utils import Readable


class MinIOStorage(Storage):
    def __init__(self, endpoint: str, bucket: str, keys: tuple[str, str] = ()):
        parts = urlparse(endpoint)
        self._minio = Minio(parts.netloc, *keys, secure="https" == parts.scheme)
        # noinspection PyProtectedMember
        self._minio._http.pools = RecentlyUsedContainer(3 * STORAGE_MAX_THREADS)
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
                    yield File(object_.object_name, size=object_.size, md5=object_.etag)
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
