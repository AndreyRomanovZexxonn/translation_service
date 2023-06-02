import asyncio

import pytest

from src.application.translation.service import TranslationService
from src.infra.provider.google.web.provider import GoogleWebTranslationProvider
from src.infra.repositories.translation.mongodb import MongoDBTranslationRepository
from src.utils.configs.app_config import AppConfiguration


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def mongodb_translation_repo(app_config: AppConfiguration) -> MongoDBTranslationRepository:
    translation_repo: MongoDBTranslationRepository = await MongoDBTranslationRepository.instance(
        config=app_config
    )
    yield translation_repo


@pytest.fixture(scope="module")
async def google_translation_provider(app_config: AppConfiguration) -> GoogleWebTranslationProvider:
    translation_provider = await GoogleWebTranslationProvider.instance(
        config=app_config
    )
    return translation_provider


@pytest.fixture(scope="module")
async def mongodb_google_translation_service(
    mongodb_translation_repo: MongoDBTranslationRepository,
    google_translation_provider: GoogleWebTranslationProvider
) -> TranslationService:
    service = TranslationService(
        translation_repo=mongodb_translation_repo,
        translation_provider=google_translation_provider
    )
    await service.initialize()
    yield service
    await mongodb_translation_repo._collection.drop()
    await service.close()
