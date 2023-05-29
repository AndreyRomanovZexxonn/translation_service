import pytest

from src.infra.provider.google.web.models import GoogleTranslatedWord
from src.infra.provider.google.web.translator import Translator


@pytest.mark.asyncio
async def test_google_web_provider():
    translator = Translator()
    results = []
    for word in ["привет", "пока"]:
        result: GoogleTranslatedWord = await translator.translate(word, dest='en', src='auto')
        results.append(result)

    assert results
