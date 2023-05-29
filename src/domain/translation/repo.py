from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import auto
from typing import Iterable, TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

from src.utils.enums import AutoName

if TYPE_CHECKING:
    from src.domain.translation.translation import Translation
    from src.utils.configs.app_config import AppConfiguration


class SortOrder(AutoName):
    ASC = auto()
    DESC = auto()


class PaginationParams(BaseModel):
    marker: Optional[str]
    limit: int = Field(
        gt=-1, default=0,
        description="Limit number of found words. 0 - means no limit."
    )


@dataclass
class TranslationRepository(ABC):
    """ Interface to access database storage with translations. """

    @classmethod
    @abstractmethod
    async def instance(cls, config: "AppConfiguration") -> "TranslationRepository":
        pass

    @abstractmethod
    async def insert(self, translation: "Translation") -> "Translation":
        pass

    @abstractmethod
    async def get(self, word: str) -> Optional["Translation"]:
        pass

    @abstractmethod
    async def delete(self, word: str) -> "Translation":
        pass

    @abstractmethod
    async def find(
            self,
            word: str,
            order: SortOrder,
            pagination: PaginationParams
    ) -> Iterable["Translation"]:
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def initialize(self):
        pass
