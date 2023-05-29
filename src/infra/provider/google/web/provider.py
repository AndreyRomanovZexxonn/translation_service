from dataclasses import dataclass

from src.domain.translation.provider import TranslationProvider
from src.domain.translation.translation import Translation
from src.infra.provider.google.web.models import GoogleTranslatedWord
from src.infra.provider.google.web.translator import Translator
from src.utils.configs.app_config import AppConfiguration


@dataclass
class GoogleWebTranslationProvider(TranslationProvider):
    """ Interface to external translation provider. """
    _translator: Translator

    @classmethod
    async def instance(cls, config: "AppConfiguration") -> "TranslationProvider":
        return cls(_translator=Translator())

    async def translate(self, word: str, to_lang: str) -> "Translation":
        result: GoogleTranslatedWord = await self._translator.translate(word, dest=to_lang, src='auto')
        return Translation(
            word=result.origin,
            word_lang=result.src,
            translation=result.text,
            translation_lang=result.dest,
            synonyms=result.synonyms
        )

    async def close(self):
        pass

    async def initialize(self):
        pass
