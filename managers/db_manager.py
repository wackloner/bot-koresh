from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


@dataclass
class DBManager:
    # TODO: store mongo url

    @cached_property
    def client(self) -> MongoClient:
        return MongoClient(port=27017)

    @cached_property
    def db(self) -> Database:
        return self.client.koresh

    @cached_property
    def users(self) -> Collection:
        return self.db.get_collection('users')
