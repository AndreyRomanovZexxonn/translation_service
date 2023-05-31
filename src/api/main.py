import logging
from typing import TYPE_CHECKING

from fastapi import FastAPI

from src.api.app import create_api
from src.api.context import set_context, ctx
from src.api.router import build_main_router
from src.utils.configs.app_config import APP_CONFIG
from src.utils.configs.env_config import ENV_CONFIG
from src.utils.logs import init_logging

init_logging(cfg=ENV_CONFIG)


if TYPE_CHECKING:
    from src.api.context import Context


app: FastAPI = create_api()

LOG = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    from src.api.context import Context
    context = await Context.instance(config=APP_CONFIG, app=app)
    set_context(context)
    await context.open()
    app.include_router(build_main_router(context))


@app.on_event("shutdown")
async def stop():
    await ctx().close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        port=APP_CONFIG.server.port,
        reload=APP_CONFIG.server.reload,
        log_config=None
    )
