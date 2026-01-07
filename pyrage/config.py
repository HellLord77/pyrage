import os
from typing import Final

STORAGE_DRY_RUN: Final[bool] = os.getenv("STORAGE_DRY_RUN", "true").lower() == "true"
STORAGE_MAX_THREADS: Final[int] = int(os.getenv("STORAGE_MAX_THREADS", "8"))

FTP_INCLUDE_HIDDEN: Final[bool] = os.getenv("FTP_INCLUDE_HIDDEN", "false").lower() == "true"

LOCAL_EXTEND_GENERATE: Final[bool] = os.getenv("LOCAL_EXTEND_GENERATE", "false").lower() == "true"

KEMONO_EXTEND_GENERATE: Final[bool] = os.getenv("KEMONO_EXTEND_GENERATE", "false").lower() == "true"
KEMONO_AUTO_SERVER: Final[bool] = os.getenv("KEMONO_AUTO_SERVER", "true").lower() == "true"

MINIO_RETRY_GENERATE: Final[bool] = os.getenv("MINIO_RETRY_GENERATE", "false").lower() == "true"

MYRIENT_EXTEND_GENERATE: Final[bool] = os.getenv("MYRIENT_EXTEND_GENERATE", "false").lower() == "true"
MYRIENT_RETRY_EXTEND_GENERATE: Final[bool] = os.getenv("MYRIENT_RETRY_EXTEND_GENERATE", "false").lower() == "true"

POKEMON_TCG_EXTEND_GENERATE: Final[bool] = os.getenv("POKEMON_TCG_EXTEND_GENERATE", "false").lower() == "true"

ROMM_FLAT_PATH: Final[bool] = os.getenv("ROMM_FLAT_PATH", "false").lower() == "true"

SFTP_AUTO_ADD: Final[bool] = os.getenv("SFTP_AUTO_ADD", "false").lower() == "true"

SOPHON_CACHE_MANIFESTS: Final[bool] = os.getenv("SOPHON_CACHE_MANIFESTS", "true").lower() == "true"

STEAM_CACHE_MANIFESTS: Final[bool] = os.getenv("STEAM_CACHE_MANIFESTS", "true").lower() == "true"

TCGDEX_EXTEND_GENERATE: Final[bool] = os.getenv("TCGDEX_EXTEND_GENERATE", "false").lower() == "true"

WAYBACK_FLAT_PATH: Final[bool] = os.getenv("WAYBACK_FLAT_PATH", "false").lower() == "true"
WAYBACK_EXTEND_GENERATE: Final[bool] = os.getenv("WAYBACK_EXTEND_GENERATE", "false").lower() == "true"

WEBDAV_DISABLE_CHECK: Final[bool] = os.getenv("WEBDAV_DISABLE_CHECK", "false").lower() == "true"
