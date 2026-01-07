from functools import lru_cache
from hashlib import md5
from typing import Iterable

from HoyoSophonDL import LauncherClient
from HoyoSophonDL import Region
from HoyoSophonDL import config
from HoyoSophonDL.help import decompress
from HoyoSophonDL.structs.SophonManifest import SophonMainAPIData
from HoyoSophonDL.structs.SophonManifest import SophonManifestProtoAsset

from ..config import SOPHON_CACHE_MANIFESTS
from ..utils import File
from ..utils import Readable
from ..utils import ReadableIterator
from . import Storage

config.configure_logger = lambda verbose=False: None


class SophonStorage(Storage):
    def __init__(self, biz: str, version: str | None = None, srcs: Iterable[str] | None = None):
        self._client = LauncherClient(region=Region.CHINESE if biz.endswith("_cn") else Region.EUROPE)
        games = self._client.get_avalibale_games()
        game = games.getByBiz(biz)
        self._branch = self._client.get_game_info(game)
        self._version = version
        self._srcs = srcs
        if SOPHON_CACHE_MANIFESTS:
            SophonMainAPIData.__hash__ = object.__hash__
            self._client.get_main_manifest = lru_cache(self._client.get_main_manifest)
            self._client.get_manifest_assets = lru_cache(self._client.get_manifest_assets)
        super().__init__()

    def _assets(self) -> Iterable[SophonManifestProtoAsset]:
        manifests = self._client.get_main_manifest(self._branch, self._version)
        for src in manifests.ManifestsIDs if self._srcs is None else self._srcs:
            manifest = manifests.getBySrc(src)
            assets = self._client.get_manifest_assets(self._branch, manifest)
            yield from assets.Assets

    def _generate_file_list(self) -> Iterable[File]:
        for asset in self._assets():
            yield File(asset.AssetFilePath, size=asset.AssetSize, md5=asset.AssetHashMd5)

    def _iterator(self, asset: SophonManifestProtoAsset) -> Iterable[bytes]:
        for chunk in asset.AssetChunks:
            # noinspection PyProtectedMember
            response = self._client._httpClient.get(chunk.ChunkUrl)
            response.raise_for_status()
            content = response.content
            if len(content) != chunk.ChunkSize:
                raise NotImplementedError
            decompressed = decompress(content)
            if (
                len(decompressed) != chunk.ChunkSizeDecompressed
                or md5(decompressed).hexdigest() != chunk.ChunkDecompressedHashMd5
            ):
                raise NotImplementedError
            yield decompressed

    def _get_file(self, file: File) -> Readable:
        for asset in self._assets():
            if asset.AssetFilePath == file.path:
                return ReadableIterator(self._iterator(asset))
        raise NotImplementedError

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
