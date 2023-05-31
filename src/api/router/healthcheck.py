from typing import TYPE_CHECKING

from fastapi import APIRouter
from starlette.responses import JSONResponse

if TYPE_CHECKING:
    pass


def build_router_healthcheck() -> APIRouter:
    router = APIRouter()

    @router.post("/")
    async def healthcheck():
        return JSONResponse(content={})

    @router.get("/")
    async def healthcheck():
        return JSONResponse(content={})

    return router
