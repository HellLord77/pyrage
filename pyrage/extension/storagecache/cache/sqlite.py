from itertools import starmap
from sqlite3 import connect
from typing import Iterator

from . import StorageCache
from ....utils import File


class SqliteStorageCache(StorageCache):
    EXTENSION = "db"

    def _dump_file_list(self):
        with connect(self._cache_path) as con:
            con.execute("DROP TABLE IF EXISTS _;")
            con.execute(
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
            con.executemany(
                """
                INSERT INTO _ (path, size, mtime, atime, ctime, md5)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                self,
            )
        con.close()

    def _load_file_list(self) -> Iterator[File]:
        with connect(self._cache_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM _;")
            yield from starmap(File, cur)
            cur.close()
