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


async def add_middlewares(application: FastAPI, context: "Context"):
    # --- CORS ---
    from starlette.middleware.cors import CORSMiddleware
    allow_origins = ["*"]
    LOG.info(f"Allowed CORS {allow_origins}")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup():
    from src.api.context import Context
    context = await Context.instance(config=APP_CONFIG)
    set_context(context)
    await context.open()
    await add_middlewares(app, context=context)
    app.include_router(build_main_router(context))
    context.app = app


@app.on_event("shutdown")
async def stop():
    await ctx().close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        port=APP_CONFIG.server.port,
        reload=APP_CONFIG.server.reload,
        debug=APP_CONFIG.server.debug,
        log_config=None,
    )
