from typing import Iterable

from requests import Session
from star_launcher_sdk import ConfigEnum
from star_launcher_sdk import Launcher
from star_launcher_sdk.config import ConfigModel

from ..config import STAR_BACKUP_CDN
from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse
from . import Storage


class StarLauncherStorage(Storage):
    def __init__(self, config: ConfigModel | ConfigEnum):
        self._launcher = Launcher(config)
        self._domain = self._launcher.get_domain()
        self._session = Session()
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        game_info = self._launcher.get_game_info()
        manifest_url = self._launcher.get_manifest_url(game_info.game_latest_version, game_info.game_latest_file_path)
        manifest = self._launcher.get_manifest(manifest_url)
        for url, file in zip(
            self._launcher.get_manifest_file_urls(self._domain, manifest, backup=STAR_BACKUP_CDN), manifest.file
        ):
            yield File(url.path[1:], size=file.size)

    def _get_file(self, file: File) -> Readable:
        cdn = self._domain.back_up_cdn if STAR_BACKUP_CDN else self._domain.primary_cdn
        return ReadableResponse(self._session.get(f"{cdn}{file.path}", stream=True))

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
