import logging
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from src.api.context import ctx, Context

if TYPE_CHECKING:
    pass

LOG = logging.getLogger(__name__)


def create_translations_router() -> APIRouter:
    router = APIRouter()

    @router.post(
        "/translate",
    )
    async def get_latest_block_number(
        context: Context = Depends(ctx)
    ):
        return {"OK": True}
    return router
