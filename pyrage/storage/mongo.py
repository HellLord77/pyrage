from io import BytesIO
from itertools import chain
from posixpath import join, split
from typing import Iterable, Optional

from bson import ObjectId, decode, encode
from bson.json_util import DEFAULT_JSON_OPTIONS, JSONOptions, dumps, loads
from pymongo import MongoClient

from ..utils import File, Readable, ReadableIterator, iter_join
from . import Storage


class MongoStorage(Storage):
    def __init__(
        self,
        database: Optional[str] = None,
        uri: Optional[str] = None,
    ):
        client = MongoClient(uri)
        self._db = (
            client.get_default_database()
            if database is None
            else client.get_database(database)
        )
        super().__init__()

    def _generate_file_list(self) -> Iterable[File]:
        for name in self._db.list_collection_names():
            for document in self._db.get_collection(name).find():
                yield File(join(name, str(document["_id"])))

    def _get_file(self, file: File) -> Readable:
        name, id_ = split(file.path)
        collection = self._db.get_collection(name)
        document = collection.find_one(ObjectId(id_))
        del document["_id"]
        return BytesIO(encode(document))

    def _set_file(self, file: File, readable: Readable):
        name, id_ = split(file.path)
        collection = self._db.get_collection(name)
        document = decode(readable.read())
        document["_id"] = ObjectId(id_)
        collection.insert_one(document)

    def _del_file(self, file: File):
        name, id_ = split(file.path)
        collection = self._db.get_collection(name)
        collection.delete_one({"_id": ObjectId(id_)})


class JSONMongoStorage(MongoStorage):
    SEP = b","
    KWARGS = {"separators": (",", ":")}

    def __init__(
        self,
        database: Optional[str] = None,
        uri: Optional[str] = None,
        json_options: JSONOptions = DEFAULT_JSON_OPTIONS,
    ):
        self._json_options = json_options
        super().__init__(database, uri)

    def _generate_file_list(self) -> Iterable[File]:
        for name in self._db.list_collection_names():
            yield File(name)

    def _get_file(self, file: File) -> Readable:
        return ReadableIterator(
            chain(
                (b"[",),
                iter_join(
                    self.SEP,
                    (
                        dumps(
                            document,
                            json_options=self._json_options,
                            **self.KWARGS,
                        ).encode()
                        for document in self._db.get_collection(file.path).find()
                    ),
                ),
                (b"]",),
            )
        )

    def _set_file(self, file: File, readable: Readable):
        collection = self._db.get_collection(file.path)
        collection.insert_many(loads(readable.read(), json_options=self._json_options))

    def _del_file(self, file: File):
        self._db.drop_collection(file.path)


class PrettyJSONMongoStorage(JSONMongoStorage):
    SEP = b",\n"
    KWARGS = {"indent": 2}
