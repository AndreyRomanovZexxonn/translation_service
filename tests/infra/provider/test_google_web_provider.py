from enum import auto
from typing import Any

import pydantic
from googletrans import Translator
from googletrans.models import Translated, TranslatedPart
from pydantic import BaseModel

from src.utils.enums import AutoLowerName


class PartOfSpeech(AutoLowerName):
    PREPOSITION = auto()
    ADVERB = auto()
    CONJUNCTION = auto()
    NOUN = auto()


class Synonyms(BaseModel):
    synonyms: dict[PartOfSpeech, dict[str, list[str]]]

    @classmethod
    def from_parsed_data(cls, data: list[list[list[Any]]]) -> "Synonyms":
        prepared_data = {}
        for item in data[3][5][0]:
            part_of_speech = item[0]
            items = {syn[0]: syn[2] for syn in item[1]}
            prepared_data[part_of_speech] = items
        return pydantic.parse_obj_as(Synonyms, {"synonyms": prepared_data})


def test_google_web_provider():
    translator = Translator()
    results = []
    for word in ["привет", "пока"]:
        result: Translated = translator.translate(word, dest='en', src='auto')
        part: TranslatedPart = result.extra_data["parts"][0]
        parsed: list = result.extra_data["parsed"]
        results.append(parsed)

    assert results
    synonyms = Synonyms.from_parsed_data(results[0])
