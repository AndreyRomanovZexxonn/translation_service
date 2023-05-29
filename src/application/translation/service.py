import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from src.domain.translation.translation import Translation

if TYPE_CHECKING:
    from src.domain.translation.repo import TranslationRepository
    from src.domain.translation.provider import TranslationProvider


LOG = logging.getLogger(__name__)


@dataclass
class TranslationService:
    translation_repo: "TranslationRepository"
    translation_provider: "TranslationProvider"

    async def close(self):
        await self.translation_repo.close()
        await self.translation_provider.close()

    async def initialize(self):
        await self.translation_repo.initialize()
        await self.translation_provider.initialize()

    async def translate(self, word: str, to_lang: str) -> Optional["Translation"]:
        if translation := await self.translation_repo.get(word=word):
            LOG.debug(f"Translation for `{word}` found in db cache")
            return translation

        if translation := await self.translation_provider.translate(
                word=word, to_lang=to_lang
        ):
            await self.translation_repo.insert(translation)
            return translation

        return None
