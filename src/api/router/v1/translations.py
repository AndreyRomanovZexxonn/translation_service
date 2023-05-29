import logging
from pydantic import Field
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.context import ctx, Context
from src.domain.translation.translation import Translation

if TYPE_CHECKING:
    pass

LOG = logging.getLogger(__name__)


class TranslationRequestDTO(BaseModel):
    word: str = Field(min_length=1)
    to_lang: str = Field(min_length=1)


def create_translations_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/translate",
        response_model=Translation
    )
    async def get_latest_block_number(
        request: TranslationRequestDTO,
        context: Context = Depends(ctx)
    ) -> Translation:
        translation: Translation = await context.translation_service.translate(
            word=request.word, to_lang=request.to_lang
        )
        if translation:
            return translation

        return None

    return router
