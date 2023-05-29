from typing import List, Optional, Any

from pydantic import BaseModel, Field, parse_obj_as

from src.domain.translation.translation import Synonyms


class TranslatedPart(BaseModel):
    text: Optional[str]
    candidates: Optional[List[str]]


class GoogleTranslatedWord(BaseModel):
    src: str = Field(default="auto", description="source language")
    dest: str = Field(default="en", description="destination language")
    origin: str = Field(description="original text")
    text: str = Field(description="translated text")
    pronunciation: Optional[str]
    parts: List[TranslatedPart]
    extra_data: Optional[dict]
    synonyms: Optional[Synonyms]

    @classmethod
    def synonyms_from_parsed_data(cls, data: list[list[list[Any]]]) -> "Synonyms":
        prepared_data = {}
        for item in data[3][5][0]:
            part_of_speech = item[0]
            items = {syn[0]: syn[2] for syn in item[1]}
            prepared_data[part_of_speech] = items
        return parse_obj_as(Synonyms, prepared_data)
