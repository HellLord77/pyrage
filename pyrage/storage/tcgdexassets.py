from functools import partial
from typing import Callable, Iterable, Optional
from urllib.parse import urlparse

from requests import Session
from tcgdexsdk import Language, TCGdex
from tcgdexsdk.enums import Extension, Quality

from ..config import TCGDEX_EXTEND_GENERATE
from ..utils import File, Readable, ReadableResponse
from . import Storage


class TCGDexAssetsStorage(Storage):
    def __init__(
        self, language: str | Language = Language.EN, endpoint: str = TCGdex.endpoint
    ):
        self._tcgdex = TCGdex(language)
        self._tcgdex.setEndpoint(endpoint)
        self._session = Session()
        super().__init__()

    def _files(self, get_url: Callable[[Extension], Optional[str]]) -> Iterable[File]:
        for extension in Extension:
            if (url := get_url(extension)) is not None:
                path = urlparse(url).path.lstrip("/")
                if TCGDEX_EXTEND_GENERATE:
                    response = self._session.head(url)
                    response.raise_for_status()
                    yield File(path, size=int(response.headers["Content-Length"]))
                else:
                    yield File(path)

    def _generate_file_list(self) -> Iterable[File]:
        for serie in self._tcgdex.serie.listSync():
            yield from self._files(serie.get_logo_url)
        for set_ in self._tcgdex.set.listSync():
            yield from self._files(set_.get_logo_url)
            yield from self._files(set_.get_symbol_url)
        for card in self._tcgdex.card.listSync():
            for quality in Quality:
                yield from self._files(partial(card.get_image_url, quality))

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(f"https://assets.tcgdex.net/{file.path}", stream=True)
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
