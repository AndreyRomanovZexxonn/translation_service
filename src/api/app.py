import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.middlewares import add_middlewares

if TYPE_CHECKING:
    pass


LOG = logging.getLogger(__name__)


def create_api() -> FastAPI:
    app = FastAPI()
    add_middlewares(application=app)

    @app.exception_handler(Exception)
    async def exception_handler(request, exc):
        LOG.error(exc, exc_info=True)
        return PlainTextResponse("Internal Server Error", status_code=500)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(exc.detail, status_code=exc.status_code)

    return app
