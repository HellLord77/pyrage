from typing import Iterable, Optional

from requests import Session

from ..utils import File, Readable, ReadableResponse
from . import Storage


class KaraokeMugenStorage(Storage):
    def __init__(
        self, collections: Optional[Iterable[str]] = None, repository: str = "kara.moe"
    ):
        self._repository = f"https://{repository}"
        self._session = Session()
        if collections is None:
            response = self._session.get(f"{self._repository}/api/karas/repository")
            response.raise_for_status()
            collections = (
                collection
                for collection, enable in response.json()["Manifest"][
                    "defaultCollections"
                ].items()
                if enable
            )
        self._collections = list(collections)
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        response = self._session.post(
            f"{self._repository}/api/karas/medias",
            json={"collections": self._collections},
        )
        response.raise_for_status()
        for kara in response.json():
            yield File(kara["mediafile"], size=kara["mediasize"])

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(
            self._session.get(
                f"{self._repository}/downloads/medias/{file.path}", stream=True
            )
        )

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
