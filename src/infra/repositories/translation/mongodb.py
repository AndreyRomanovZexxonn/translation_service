import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Optional

import pydantic
import pymongo
from bson import CodecOptions
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import TEXT

from src.domain.translation.repo import (
    TranslationRepository, SortOrder, PaginationParams
)
from src.domain.translation.translation import Translation, WORD, TRANSLATIONS, DEFINITIONS, EXAMPLES
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
    async def instance(cls, config: "AppConfiguration") -> "MongoDBTranslationRepository":
        _client: "AsyncIOMotorClient" = await cls._configure_client(config.mongodb)
        _db: "AsyncIOMotorDatabase" = _client.get_database(config.mongodb.db)
        _collection: "AsyncIOMotorCollection" = _db.get_collection(
            config.mongodb.collection, codec_options=CodecOptions(tz_aware=True)
        )
        LOG.info(f"MongoDB: db={config.mongodb.db}, collection={config.mongodb.collection}")
        return cls(_client=_client, _db=_db, _collection=_collection)

    async def get(self, word: str) -> Optional["Translation"]:
        doc = await self._collection.find_one({WORD: word})
        return doc and pydantic.parse_obj_as(Translation, doc)

    async def insert(self, translation: "Translation"):
        await self._collection.insert_one(translation.dict())

    async def delete(self, word: str) -> bool:
        result = await self._collection.delete_one({WORD: word})
        return result.deleted_count > 0

    async def find(
            self,
            word: Optional[str],
            order: SortOrder = SortOrder.ASC,
            pagination: PaginationParams = None,
            exclude_translations: bool = True,
            exclude_definitions: bool = True,
            exclude_examples: bool = True
    ) -> Iterable["Translation"]:

        pagination = pagination or PaginationParams()
        projection = {}
        if exclude_translations:
            projection[TRANSLATIONS] = 0
        if exclude_definitions:
            projection[DEFINITIONS] = 0
        if exclude_examples:
            projection[EXAMPLES] = 0

        if order is SortOrder.DESC:
            ordering = pymongo.DESCENDING
        else:
            ordering = pymongo.ASCENDING

        query = {WORD: {"$gt": pagination.marker}}
        if word:
            query[WORD]["$regex"] = f".*{word}.*"

        batch_size = 1000
        cursor = self._collection.find(
            query, projection=projection
        ).limit(
            pagination.limit
        ).sort(WORD, ordering)
        results: list[Translation] = []
        while docs := await cursor.to_list(length=batch_size):
            print(docs)
            results.extend(
                pydantic.parse_obj_as(Translation, doc) for doc in docs
            )

        return results

    async def close(self):
        self._client.close()
        LOG.info("MongoDB: connection closed")

    async def initialize(self):
        index = await self._collection.create_index(
            [(WORD, TEXT), (WORD, pymongo.ASCENDING)], unique=True, background=True
        )
        LOG.info(f"MongoDB: creating index `{index}` on `{WORD}` field")

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
