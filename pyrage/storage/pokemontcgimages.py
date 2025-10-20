from http import HTTPStatus
from typing import Iterable, Optional
from urllib.parse import urlparse

from pokemontcgsdk import Card, RestClient, Set, querybuilder
from requests import HTTPError, Session

from ..config import POKEMON_TCG_EXTEND_GENERATE
from ..utils import File, Readable, ReadableResponse
from . import Storage


class PokemonTCGImagesStorage(Storage):
    def __init__(
        self, api_key: Optional[str] = None, endpoint: str = querybuilder.__endpoint__
    ):
        RestClient.configure(api_key)
        querybuilder.__endpoint__ = endpoint
        self._session = Session()
        super().__init__()

    def _file(self, url: str) -> Optional[File]:
        path = urlparse(url).path.lstrip("/")
        if POKEMON_TCG_EXTEND_GENERATE:
            response = self._session.head(url)
            try:
                response.raise_for_status()
            except HTTPError:  # FIXME https://images.pokemontcg.io/mcd17/1.png
                if response.status_code != HTTPStatus.NOT_FOUND:
                    raise
            else:
                return File(path, size=int(response.headers["Content-Length"]))
        else:
            return File(path)

    def _generate_file_list(self) -> Iterable[File]:
        for set_ in Set.all():
            yield from filter(
                None,
                map(
                    self._file,
                    (
                        set_.images.symbol,
                        set_.images.logo,
                    ),
                ),
            )
        for card in Card.all():
            yield from filter(
                None,
                map(
                    self._file,
                    (
                        card.images.small,
                        card.images.large,
                    ),
                ),
            )

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(f"https://images.pokemontcg.io/{file.path}", stream=True)
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
