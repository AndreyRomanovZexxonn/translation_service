import pytest

from src.application.translation.service import TranslationService
from src.domain.translation.translation import Translation
from src.infra.provider.google.web.constants import Lang


@pytest.mark.asyncio
async def test_translation_service(translation_service: TranslationService):
    translation: "Translation" = await translation_service.translate(
        word="channel", dst_lang=Lang.RU
    )
    assert translation.word == "channel"
    assert translation.word_lang == "en"
    assert translation.translation == "канал"
    assert translation.translation_lang == "ru"
    assert translation.translations
