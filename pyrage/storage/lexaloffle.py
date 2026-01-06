from collections.abc import Iterable
from http import HTTPStatus
from itertools import compress
from re import compile

from requests import HTTPError
from requests import Session

from ..utils import File
from ..utils import Readable
from ..utils import ReadableResponse
from . import Storage


class LexaloffleStorage(Storage):
    _OWNER_MAP = {
        "pico-8": ("7wdekp", "7tiann"),
        "voxatron": ("5r8npa",),
        "picotron": ("8pwrtp",),
    }
    _PAT_VERSION = compile(r"[\s^]\s*v?(?P<ver>\d+\.\d+\.\d+[a-z]?)\s*[\s$]")
    _VOXATRON_VERSIONS = (
        "0.3.5",
        "0.3.4",
        "0.3.3",
        "0.3.2",
        "0.3.1",
        "0.3.0",
        "0.2.13",
        "0.2.12",
        "0.2.11",
        "0.2.10",
        "0.2.9",
        "0.2.8",
        "0.2.7",
        "0.2.6",
        "0.2.5",
        "0.2.4",
        "0.2.3",
        "0.2.2",
        "0.2.1",
        "0.2.0",
    )

    def __init__(self, pico_8: bool = True, voxatron: bool = True, picotron: bool = True):
        self._session = Session()
        self._pico_8 = pico_8
        self._voxatron = voxatron
        self._picotron = picotron
        super().__init__()

    def _files(self, project: str, version: str) -> Iterable[File]:
        for suffix in (
            "setup.exe",
            "windows.zip",
            "i386.zip",
            "amd64.zip",
            "osx.zip",
            "raspi.zip",
            "chip.zip",
        ):
            for owner in self._OWNER_MAP[project]:
                path = f"{owner}/{project}_{version}_{suffix}"
                response = self._session.head(f"https://www.lexaloffle.com/dl/{path}")
                try:
                    response.raise_for_status()
                except HTTPError:
                    if response.status_code != HTTPStatus.NOT_FOUND:
                        raise
                else:
                    yield File(path, size=int(response.headers["Content-Length"]))

    def _generate_file_list(self) -> Iterable[File]:
        for project in compress(
            ("pico-8", "voxatron", "picotron"),
            (self._pico_8, self._voxatron, self._picotron),
        ):
            if project == "voxatron":
                for version in self._VOXATRON_VERSIONS:
                    yield from self._files(project, version)
            else:
                response = self._session.get(f"https://www.lexaloffle.com/dl/docs/{project}_changelog.txt")
                response.raise_for_status()
                for match in self._PAT_VERSION.finditer(response.text):
                    yield from self._files(project, match.group("ver"))

    def _get_file(self, file: File) -> Readable:
        return ReadableResponse(self._session.get(f"https://www.lexaloffle.com/dl/{file.path}", stream=True))

    def _set_file(self, file: File, readable: Readable):
        raise NotImplementedError

    def _del_file(self, file: File):
        raise NotImplementedError
