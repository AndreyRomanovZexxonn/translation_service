import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Optional

from bson import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient

from src.domain.translation.repo import (
    TranslationRepository, SortOrder, PaginationParams
)
from src.domain.translation.translation import Translation
from src.utils.configs.app_config import AppConfiguration

if TYPE_CHECKING:
    from src.infra.repositories.mongodb.configuration import (
        MongodbConfiguration
    )
    from motor.motor_asyncio import (
        AsyncIOMotorDatabase, AsyncIOMotorCollection
    )


LOG = logging.getLogger(__name__)


@dataclass
class MongoDBTranslationRepository(TranslationRepository):
    _client: "AsyncIOMotorClient"
    _db: "AsyncIOMotorDatabase"
    _collection: "AsyncIOMotorCollection"

    @classmethod
    async def instance(cls, config: "AppConfiguration") -> "TranslationRepository":
        _client: "AsyncIOMotorClient" = await cls._configure_client(config.mongodb)
        _db: "AsyncIOMotorDatabase" = _client.get_database(config.mongodb.db)
        _collection: "AsyncIOMotorCollection" = _db.get_collection(
            config.mongodb.collection, codec_options=CodecOptions(tz_aware=True)
        )
        return cls(_client=_client, _db=_db, _collection=_collection)

    async def get(self, word: str) -> Optional["Translation"]:
        pass

    async def insert(self, translation: "Translation") -> "Translation":
        pass

    async def delete(self, word: str) -> "Translation":
        pass

    async def find(
            self,
            word: str,
            order: SortOrder,
            pagination: PaginationParams
    ) -> Iterable["Translation"]:
        pass

    async def close(self):
        self._client.close()
        LOG.info("MongoDB connection closed")

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
