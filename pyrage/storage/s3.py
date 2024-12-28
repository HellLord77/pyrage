from typing import Iterable
from typing import Optional

from boto3 import client
from botocore import UNSIGNED
from botocore.config import Config

from . import Storage
from ..utils import File
from ..utils import Readable


class S3Storage(Storage):
    endpoint_url = None

    def __init__(
        self,
        bucket: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        config = None
        if aws_secret_access_key is None or aws_access_key_id is None:
            config = Config(signature_version=UNSIGNED)
        self._s3 = client(
            "s3",
            endpoint_url=self.endpoint_url,
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
                    md5=etag if len(etag := content["ETag"]) == 32 else None,
                )

    def _get_file(self, file: File) -> Readable:
        return self._s3.get_object(Bucket=self._bucket, Key=file.path)["Body"]

    def _set_file(self, file: File, readable: Readable):
        # noinspection PyTypeChecker
        self._s3.put_object(Bucket=self._bucket, Key=file.path, Body=readable)

    def _del_file(self, file: File):
        self._s3.delete_object(Bucket=self._bucket, Key=file.path)


class MinIOS3Storage(S3Storage):
    def __init__(
        self,
        endpoint: str,
        bucket: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.endpoint_url = endpoint
        super().__init__(
            bucket,
            access_key,
            secret_key,
        )
