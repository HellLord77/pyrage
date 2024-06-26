from itertools import starmap
from sqlite3 import connect
from typing import Iterator

from . import StorageCache
from ....utils import File


class SqliteStorageCache(StorageCache):
    EXTENSION = "db"

    def _dump_file_list(self):
        with connect(self._cache_path) as con:
            cur = con.cursor()
            cur.execute(
                """
                DROP TABLE IF EXISTS _;
                """
            )
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
                self,
            )
            cur.close()
        con.close()

    def _load_file_list(self) -> Iterator[File]:
        with connect(self._cache_path) as con:
            yield from starmap(
                File,
                con.execute(
                    """
                    SELECT * FROM _;
                    """
                ),
            )
        con.close()
