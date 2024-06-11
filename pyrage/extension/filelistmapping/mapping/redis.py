from ast import literal_eval
from itertools import islice
from typing import Iterator
from typing import Optional

from redis import Redis

from . import FileListMapping
from ....utils import File


class RedisFileListMapping(FileListMapping):
    def __init__(self, *args, mapping_url: Optional[str] = None, **kwargs):
        self._mapping = Redis() if mapping_url is None else Redis.from_url(mapping_url)
        self.clear()
        super().__init__(*args, **kwargs)
        self._file_list = self

    def __len__(self):
        return self._mapping.dbsize()

    def __contains__(self, key: str) -> bool:
        return self._mapping.exists(key)

    def __iter__(self) -> Iterator[str]:
        return map(bytes.decode, self._mapping.scan_iter())

    def __getitem__(self, key: str) -> File:
        return File(key, *literal_eval(self._mapping[key].decode()))

    def __setitem__(self, key: str, value: File):
        self._mapping[key] = ",".join(map(repr, islice(value, 1, None)))

    def __delitem__(self, key: str):
        if not self._mapping.delete(key):
            raise KeyError(key)

    def clear(self):
        self._mapping.flushdb()
