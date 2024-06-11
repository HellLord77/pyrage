from itertools import starmap
from os import remove
from sqlite3 import connect
from typing import Iterable
from typing import Iterator
from typing import TextIO

from . import StorageCache
from ....utils import File


class SqliteStorageCache(StorageCache):
    EXTENSION = "db"

    @staticmethod
    def _dump_file_list(writable: TextIO, files: Iterable[File]):
        writable.close()
        remove(writable.name)
        with connect(writable.name) as con:
            cur = con.cursor()
            cur.execute(
                """
                CREATE TABLE _ (
                    path TEXT PRIMARY KEY NOT NULL,
                    size INTEGER,
                    mtime REAL,
                    atime REAL,
                    ctime REAL,
                    md5 VARCHAR(32)
                );
                """
            )
            cur.executemany(
                """
                INSERT INTO _ (path, size, mtime, atime, ctime, md5)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                files,
            )
            cur.close()

    @staticmethod
    def _load_file_list(readable: TextIO) -> Iterator[File]:
        readable.close()
        with connect(readable.name) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM _;")
            yield from starmap(File, cur)
            cur.close()
