from dataclasses import dataclass

from src.domain.translation.provider import TranslationProvider
from src.domain.translation.translation import Translation
from src.utils.configs.app_config import AppConfiguration


@dataclass
class GoogleWebTranslationProvider(TranslationProvider):
    """ Interface to external translation provider. """

    @classmethod
    async def instance(cls, config: "AppConfiguration") -> "TranslationProvider":
        pass

    async def translate(self, word: str, to_lang: str) -> "Translation":
        pass

    async def close(self):
        pass

    async def initialize(self):
        pass
