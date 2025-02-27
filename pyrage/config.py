import os
from typing import Final

STORAGE_DRY_RUN: Final[bool] = os.getenv("STORAGE_DRY_RUN", "true").lower() == "true"
STORAGE_MAX_THREADS: Final[int] = int(os.getenv("STORAGE_MAX_THREADS", "8"))

FTP_INCLUDE_HIDDEN: Final[bool] = (
    os.getenv("FTP_INCLUDE_HIDDEN", "false").lower() == "true"
)

SFTP_AUTO_ADD: Final[bool] = os.getenv("SFTP_AUTO_ADD", "false").lower() == "true"

WEBDAV_DISABLE_CHECK: Final[bool] = (
    os.getenv("WEBDAV_DISABLE_CHECK", "false").lower() == "true"
)

MINIO_RETRY_GENERATE: Final[bool] = (
    os.getenv("MINIO_RETRY_GENERATE", "false").lower() == "true"
)

STEAM_CACHE_MANIFESTS: Final[bool] = (
    os.getenv("STEAM_CACHE_MANIFESTS", "true").lower() == "true"
)
