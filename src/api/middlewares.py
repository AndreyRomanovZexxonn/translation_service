import logging
from typing import TYPE_CHECKING

from starlette.middleware.gzip import GZipMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI


LOG = logging.getLogger(__name__)


def add_middlewares(application: "FastAPI"):
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

    application.add_middleware(GZipMiddleware)
