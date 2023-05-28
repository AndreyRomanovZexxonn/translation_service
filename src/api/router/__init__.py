from typing import TYPE_CHECKING

from fastapi import APIRouter

from src.api.router.v1 import build_router_v1

if TYPE_CHECKING:
    from src.api.context import Context


def build_main_router(context: "Context") -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(router=build_router_v1(context), prefix="/api/v1")
    return api_router
