import logging
from typing import Iterable
from urllib.parse import urlparse
from uuid import uuid4

from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import InvalidResponseError
from minio.helpers import DictType
from minio.helpers import MAX_PART_SIZE
from urllib3 import BaseHTTPResponse

# noinspection PyProtectedMember
from urllib3._collections import RecentlyUsedContainer

from pyrage.config import MINIO_BYPASS_CACHE
from pyrage.config import STORAGE_MAX_THREADS
from pyrage.storage import Storage
from pyrage.utils import File
from pyrage.utils import Readable

logger = logging.getLogger(__name__)


class _MinioBypassCache(Minio):
    def _url_open(
        self,
        method: str,
        region: str,
        bucket_name: str | None = None,
        object_name: str | None = None,
        body: bytes | None = None,
        headers: DictType | None = None,
        query_params: DictType | None = None,
        preload_content: bool = True,
        no_body_trace: bool = False,
    ) -> BaseHTTPResponse:
        if query_params is None:
            query_params = {}
        query_params[uuid4().hex] = uuid4().hex
        return super()._url_open(
            method,
            region,
            bucket_name,
            object_name,
            body,
            headers,
            query_params,
            preload_content,
            no_body_trace,
        )


class MinIOStorage(Storage):
    def __init__(self, endpoint: str, bucket: str, keys: tuple[str, str] = ()):
        parts = urlparse(endpoint)
        self._minio = (_MinioBypassCache if MINIO_BYPASS_CACHE else Minio)(
            parts.netloc, *keys, secure="https" == parts.scheme
        )
        # noinspection PyProtectedMember
        self._minio._http.pools = RecentlyUsedContainer(3 * STORAGE_MAX_THREADS)
        self._bucket = bucket
        super().__init__()

    def get_file_list(self) -> dict[str, File]:
        start_after = None
        object_ = None
        while True:
            try:
                for object_ in self._minio.list_objects(
                    self._bucket, recursive=True, start_after=start_after
                ):
                    # noinspection PyArgumentList
                    self._add_file_list(
                        File(object_.object_name, size=object_.size, md5=object_.etag)
                    )
            except InvalidResponseError:
                if object_ is not None:
                    start_after = object_.object_name
                logger.error("[!] %s", start_after)
            else:
                break
        return super().get_file_list()

    def __get_file_list(self) -> dict[str, File]:
        prefixes = [""]
        while prefixes:
            for object_ in self._minio.list_objects(
                self._bucket, prefix=prefixes.pop(0)
            ):
                if object_.is_dir:
                    prefixes.append(object_.object_name)
                else:
                    # noinspection PyArgumentList
                    self._add_file_list(
                        File(object_.object_name, size=object_.size, md5=object_.etag)
                    )
        return super().get_file_list()

    def _get_file(self, file: File) -> Readable:
        return self._minio.get_object(self._bucket, file.path)

    def _set_file(self, file: File, readable: Readable):
        # noinspection PyTypeChecker
        self._minio.put_object(
            self._bucket, file.path, readable, -1, part_size=MAX_PART_SIZE
        )

    def _del_file(self, file: File):
        self._minio.remove_object(self._bucket, file.path)

    def _del_files(self, files: Iterable[File]):
        self._minio.remove_objects(
            self._bucket, (DeleteObject(file.path) for file in files)
        )
