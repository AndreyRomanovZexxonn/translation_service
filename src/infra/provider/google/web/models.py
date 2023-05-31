from collections import defaultdict
from typing import List, Optional, Any, Iterable

from pydantic import BaseModel, Field, parse_obj_as

from src.domain.translation.translation import Translations, Definitions, PartOfSpeech, Definition
from src.infra.provider.google.web.constants import Lang


class TranslatedPart(BaseModel):
    text: Optional[str]
    candidates: Optional[List[str]]


class GoogleTranslatedWord(BaseModel):
    src: str = Field(default="auto", description="source language")
    dest: Lang = Field(default=Lang.EN, description="destination language")
    origin: str = Field(description="original text")
    text: str = Field(description="translated text")
    pronunciation: Optional[str]
    parts: List[TranslatedPart]
    extra_data: Optional[dict]
    translations: Optional[Translations]
    definitions: Optional[Definitions]
    examples: Optional[list[str]]

    @classmethod
    def translations_from_parsed_data(cls, data: list[list[list[Any]]]) -> "Translations":
        prepared_data = {}
        for item in data[3][5][0]:
            part_of_speech = item[0]
            items = {syn[0]: syn[2] for syn in item[1]}
            prepared_data[part_of_speech] = items
        return parse_obj_as(Translations, prepared_data)

    @classmethod
    def definitions_from_parsed_data(cls, data: list[list[list[Any]]]) -> "Definitions":
        prepared_data = defaultdict(list)
        for group in data[3][1][0]:
            part_of_speech = group[0]
            for items in group[1]:
                definition, example, *other = items
                tags, synonyms = None, None
                if len(other) > 3:
                    if _synonyms := cls._flatten_iterables(other[-1]):
                        synonyms = list(_synonyms)
                else:
                    if _tags := cls._flatten_iterables(other[-1]):
                        tags = list(_tags)
                prepared_data[part_of_speech].append(
                    Definition(
                        text=definition,
                        example=example,
                        tags=tags,
                        synonyms=synonyms
                    )
                )
        return parse_obj_as(Definitions, prepared_data)

    @classmethod
    def examples_from_parsed_data(cls, data: list[list[list[Any]]]) -> list[str]:
        return [item[1] for item in data[3][2][0]]

    @classmethod
    def _flatten_iterables(cls, value):
        if not isinstance(value, Iterable):
            return None
        return cls._flatten_nested_iterables(value)

    @classmethod
    def _flatten_nested_iterables(cls, value):
        match value:
            case (list() | tuple() | set()) as items:
                for item in items:
                    yield from cls._flatten_iterables(item)
            case _:
                yield value
