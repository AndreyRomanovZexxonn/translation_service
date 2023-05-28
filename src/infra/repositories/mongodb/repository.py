import logging
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pymongo
from bson import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient

if TYPE_CHECKING:
    from src.infra.repositories.mongodb.configuration import MongodbConfiguration
    from pymongo.collection import Collection as MongoCollection
    from pymongo.database import Database as MongoDatabase
    from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection


MONGODB_ID: str = "_id"
LOG = logging.getLogger(__name__)


@dataclass
class MongodbRepository(ABC):
    _client: "AsyncIOMotorClient"
    _db: "AsyncIOMotorDatabase"
    _collection: "AsyncIOMotorCollection"

    @classmethod
    async def instance(cls, config: MongodbConfiguration) -> "MongodbRepository":
        _client: "AsyncIOMotorClient" = await cls._configure_client(config)
        _db: "AsyncIOMotorDatabase" = _client.get_database(config.db)
        _collection: "AsyncIOMotorCollection" = _db.get_collection(
            config.collection, codec_options=CodecOptions(tz_aware=True)
        )
        return cls(_client=_client, _db=_db, _collection=_collection)

    async def close(self):
        await self._client.close()

    @abstractmethod
    async def put(self, key, value):
        pass

    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def initialize(self):
        pass

    @classmethod
    async def _configure_client(cls, config: "MongodbConfiguration") -> "AsyncIOMotorClient":
        client = AsyncIOMotorClient(
            host=config.url,
            username=config.username,
            password=config.password
        )
        info: dict = await client.server_info()
        version = info["version"]
        LOG.info(f"Connected to MongoDB server, {version=}")
        return client
