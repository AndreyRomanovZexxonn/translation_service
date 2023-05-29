from typing import Optional

from pydantic import BaseModel, Field


class Translation(BaseModel):
    word: str
    word_lang: Optional[str]

    translation: str
    translation_lang: str = Field(default="en-US", const=True)
