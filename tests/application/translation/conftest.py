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
async def translation_service(app_config: AppConfiguration) -> TranslationService:
    translation_repo = await MongoDBTranslationRepository.instance(
        config=app_config
    )
    translation_provider = await GoogleWebTranslationProvider.instance(
        config=app_config
    )

    service = TranslationService(
        translation_repo=translation_repo,
        translation_provider=translation_provider
    )
    await service.initialize()
    yield service
    await service.close()
