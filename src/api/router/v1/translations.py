import logging
from pydantic import Field
from typing import TYPE_CHECKING, Iterable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse

from src.api.context import ctx, Context
from src.domain.translation.repo import SortOrder, PaginationParams
from src.domain.translation.translation import Translation

if TYPE_CHECKING:
    pass

LOG = logging.getLogger(__name__)


class TranslationRequestDTO(BaseModel):
    word: str = Field(min_length=1)
    to_lang: str = Field(min_length=1)


class DeleteRequestDTO(BaseModel):
    word: str = Field(min_length=1)


class ListRequestDTO(BaseModel):
    word: str = Field(min_length=1)
    order: SortOrder = SortOrder.ASC
    pagination: PaginationParams = Field(default_factory=lambda: PaginationParams())
    exclude_synonyms: bool = True


def create_translations_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/translate",
        response_model=Translation
    )
    async def translate_word(
        request: TranslationRequestDTO,
        context: Context = Depends(ctx)
    ) -> Translation:
        translation: Translation = await context.translation_service.translate(
            word=request.word, to_lang=request.to_lang
        )
        if translation:
            return translation

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRANSLATION_NOT_FOUND"}
        )

    @router.post(
        "/delete"
    )
    async def delete_word(
        request: DeleteRequestDTO,
        context: Context = Depends(ctx)
    ):
        translation: Translation = await context.translation_service.translation_repo.delete(
            word=request.word
        )
        if translation:
            return JSONResponse(content={"OK": True})

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "TRANSLATION_NOT_FOUND"}
        )

    @router.post(
        "/list",
        response_model=list[Translation]
    )
    async def list_translations(
        request: ListRequestDTO,
        context: Context = Depends(ctx)
    ) -> list[Translation]:
        translations: Iterable[Translation] = await context.translation_service.translation_repo.find(
            word=request.word,
            order=request.order,
            pagination=request.pagination,
            exclude_synonyms=request.exclude_synonyms
        )
        return list(translations)

    return router
