from itertools import batched
from typing import Iterable
from typing import Optional

from boto3 import client
from botocore import UNSIGNED
from botocore.config import Config

from . import Storage
from ..utils import File
from ..utils import Readable
from ..utils import SeekableReadable
from ..utils import is_seekable


class S3Storage(Storage):
    def __init__(
        self,
        bucket: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        config = None
        if aws_secret_access_key is None or aws_access_key_id is None:
            config = Config(signature_version=UNSIGNED)
        self._s3 = client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=config,
        )
        self._bucket = bucket
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for response in self._s3.get_paginator("list_objects_v2").paginate(
            Bucket=self._bucket
        ):
            try:
                contents = response["Contents"]
            except KeyError:
                break
            for content in contents:
                yield File(
                    content["Key"],
                    size=content["Size"],
                    mtime=content["LastModified"].timestamp(),
                    md5=(
                        etag
                        if len(etag := content["ETag"].replace('"', "")) == 32
                        else None
                    ),
                )

    def _get_file(self, file: File) -> Readable:
        return self._s3.get_object(Bucket=self._bucket, Key=file.path)["Body"]

    def _set_file(self, file: File, readable: Readable):
        if not is_seekable(readable):
            readable = SeekableReadable(readable)
        # noinspection PyTypeChecker
        self._s3.put_object(Bucket=self._bucket, Key=file.path, Body=readable)

    def _del_file(self, file: File):
        self._s3.delete_object(Bucket=self._bucket, Key=file.path)

    def _del_files(self, files: Iterable[File]):
        for batch in batched(files, 1000):
            self._s3.delete_objects(
                Bucket=self._bucket,
                Delete={"Objects": [{"Key": file.path} for file in batch]},
            )
