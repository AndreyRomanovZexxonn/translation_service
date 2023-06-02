import pytest

from src.infra.provider.google.web.constants import Lang
from src.infra.provider.google.web.models import GoogleTranslatedWord
from src.infra.provider.google.web.translator import Translator


@pytest.mark.asyncio
async def test_google_web_provider():
    translator = Translator()
    result: GoogleTranslatedWord = await translator.translate("channel", dest=Lang.RU)
    assert result
