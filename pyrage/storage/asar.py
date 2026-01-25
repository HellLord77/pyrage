from pathlib import Path
from threading import Lock
from typing import Iterable

from asar import AsarArchive
from asar.metadata import Type

from ..utils import File
from ..utils import Readable
from . import Storage


class AsarStorage(Storage):
    def __init__(self, asar: Path):
        self._asar = AsarArchive(asar, "r")
        self._asar.__enter__()
        self._lock = Lock()
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for meta in self._asar.metas:
            if meta.type == Type.FILE:
                yield File(meta.path.as_posix(), size=meta.size, sha256=meta.integrity["hash"])

    def _get_file(self, file: File) -> Readable:
        node = self._asar._search_node_from_path(Path(file.path), False)
        if node.unpacked:
            return node.file_path.open("rb")
        else:
            file_reader = node.file_reader
            file_reader._reader = self._asar.asar.open("rb")
            try:
                file_reader.seek(0)
            except ValueError:
                pass
            return file_reader

    def _set_file(self, file: File, readable: Readable):
        with self._lock, AsarArchive(self._asar.asar, "w") as archive:
            archive.pack_stream(Path(file.path), readable)

    def _del_file(self, file: File):
        raise NotImplementedError
