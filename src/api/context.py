import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from src.application.translation.service import TranslationService
from src.infra.provider.google.web.provider import GoogleWebTranslationProvider
from src.infra.repositories.translation.repo import MongoDBTranslationRepository
from src.utils.configs.app_config import AppConfiguration
from src.utils.enums import EnvType

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


@dataclass
class Context:
    env: EnvType
    translation_service: "TranslationService"

    @classmethod
    async def instance(cls, config: AppConfiguration):
        translation_repo = await MongoDBTranslationRepository.instance(
            config=config
        )
        translation_provider = await GoogleWebTranslationProvider.instance(
            config=config
        )
        translation_service = TranslationService(
            translation_repo=translation_repo,
            translation_provider=translation_provider
        )
        return cls(
            env=config.env,
            translation_service=translation_service
        )

    async def open(self):
        await self.translation_service.initialize()

    async def close(self):
        await self.translation_service.close()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            logging.exception(f"{exc_type}, {exc_val}, {exc_tb}")
        await self.close()
        return self


_current_context = None


def set_context(context: Context, overwrite: bool = False):
    global _current_context
    if not overwrite:
        assert _current_context is None

    _current_context = context


def ctx() -> Optional[Context]:
    global _current_context
    return _current_context
