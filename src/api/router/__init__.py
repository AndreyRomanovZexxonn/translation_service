from typing import TYPE_CHECKING

from fastapi import APIRouter

from src.api.router.healthcheck import build_router_healthcheck
from src.api.router.v1 import build_router_v1

if TYPE_CHECKING:
    from src.api.context import Context


def build_main_router(context: "Context") -> APIRouter:
    api_router = APIRouter()
    api_router.include_router(router=build_router_v1(context), prefix="/api/v1", tags=["API"])
    api_router.include_router(router=build_router_healthcheck(), prefix="/healthcheck", tags=["Utils"])
    return api_router
