from enum import auto
from typing import Optional

from pydantic import BaseModel, Field

from src.infra.provider.google.web.constants import Lang
from src.utils.enums import AutoLowerName


class PartOfSpeech(AutoLowerName):
    NOUN = auto()
    PRONOUN = auto()
    VERB = auto()
    ADJECTIVE = auto()
    ADVERB = auto()
    PREPOSITION = auto()
    CONJUNCTION = auto()
    ABBREVIATION = auto()
    INTERJECTION = auto()
    EXCLAMATION = auto()


class Definition(BaseModel):
    text: str
    example: Optional[str]
    tags: Optional[list[str]]
    synonyms: Optional[list[str]]


Translations = dict[PartOfSpeech, dict[str, list[str]]]
Definitions = dict[PartOfSpeech, list[Definition]]

WORD = "word"
TRANSLATIONS = "translations"
DEFINITIONS = "definitions"
EXAMPLES = "examples"


class Translation(BaseModel):
    word: str = Field(alias=WORD)
    word_lang: Optional[str]

    translation: str
    translation_lang: Lang = Lang.EN

    translations: Optional[Translations] = Field(alias=TRANSLATIONS)
    definitions: Optional[Definitions] = Field(alias=DEFINITIONS)
    examples: Optional[list[str]] = Field(alias=EXAMPLES)

    class Config:
        allow_population_by_field_name = False
        use_enum_values = True
