from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.domain.translation.translation import Translation
    from src.utils.configs.app_config import AppConfiguration


@dataclass
class TranslationProvider(ABC):
    """ Interface to external provider provider. """

    @classmethod
    @abstractmethod
    async def instance(cls, config: "AppConfiguration") -> "TranslationProvider":
        pass

    @abstractmethod
    async def translate(self, word: str, to_lang: str) -> "Translation":
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def initialize(self):
        pass
