import logging
from collections import defaultdict
from typing import List, Optional, Any, Iterable

import pydantic
from pydantic import BaseModel, Field, parse_obj_as

from src.domain.translation.translation import Translations, Definitions, PartOfSpeech, Definition
from src.infra.provider.google.web.constants import Lang


LOG = logging.getLogger(__name__)


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
    def translations_from_parsed_data(cls, data: list[list[list[Any]]]) -> Optional["Translations"]:
        prepared_data = {}
        for item in data[3][5][0]:
            part_of_speech = item[0]
            items = {syn[0]: syn[2] for syn in item[1]}
            prepared_data[part_of_speech] = items
        try:
            return parse_obj_as(Translations, prepared_data)
        except pydantic.ValidationError as ex:
            LOG.error(f"Failed to parse translations: {ex}")
            return None

    @classmethod
    def definitions_from_parsed_data(cls, data: list[list[list[Any]]]) -> Optional["Definitions"]:
        prepared_data = defaultdict(list)
        for group in data[3][1][0]:
            part_of_speech = group[0]
            for items in group[1]:
                try:
                    definition, example, *other = items
                except ValueError:
                    definition = items[0]
                    example = None
                    other = []

                tags, synonyms = None, None
                if len(other) > 3:
                    if _synonyms := cls._flatten_iterables(other[-1]):
                        synonyms = list(_synonyms)
                else:
                    if other and (_tags := cls._flatten_iterables(other[-1])):
                        tags = list(_tags)
                prepared_data[part_of_speech].append(
                    Definition(
                        text=definition,
                        example=example,
                        tags=tags,
                        synonyms=synonyms
                    )
                )
        try:
            return parse_obj_as(Definitions, prepared_data)
        except pydantic.ValidationError as ex:
            LOG.error(f"Failed to parse definitions: {ex}")
            return None

    @classmethod
    def examples_from_parsed_data(cls, data: list[list[list[Any]]]) -> Optional[list[str]]:
        try:
            examples_raw = data[3][2][0]
        except (TypeError, IndexError):
            return None
        return [item[1] for item in examples_raw]

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
