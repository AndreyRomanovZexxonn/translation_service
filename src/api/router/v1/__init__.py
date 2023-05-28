from typing import TYPE_CHECKING

from fastapi import APIRouter

from src.api.router.v1.translations import create_translations_router

if TYPE_CHECKING:
    from src.api.context import Context


def build_router_v1(context: "Context") -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(
        router=create_translations_router(), prefix="/translations"
    )
    return api_router
