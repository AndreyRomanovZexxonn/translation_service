import pytest

from src.infra.provider.google.web.constants import Lang
from src.infra.provider.google.web.models import GoogleTranslatedWord
from src.infra.provider.google.web.translator import Translator


@pytest.fixture()
async def x():
    return 1


@pytest.mark.asyncio
async def test_google_web_provider(x):
    assert isinstance(x, int)
    translator = Translator()
    result: GoogleTranslatedWord = await translator.translate("channel", dest=Lang.RU)
    assert result
