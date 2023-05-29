from enum import auto
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.enums import AutoLowerName


class PartOfSpeech(AutoLowerName):
    PREPOSITION = auto()
    ADVERB = auto()
    CONJUNCTION = auto()
    NOUN = auto()


Synonyms = dict[PartOfSpeech, dict[str, list[str]]]

WORD = "word"
SYNONYMS = "synonyms"


class Translation(BaseModel):
    word: str = Field(alias=WORD)
    word_lang: Optional[str]

    translation: str
    translation_lang: str = Field(default="en", const=True)

    synonyms: Optional[Synonyms] = Field(alias=SYNONYMS)

    class Config:
        allow_population_by_field_name = False
        use_enum_values = True
