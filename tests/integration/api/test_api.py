import asyncio
import json
from pathlib import Path
from pprint import pformat
from typing import TYPE_CHECKING

import pytest
from deepdiff import DeepDiff
from httpx import AsyncClient
from humanfriendly.text import random_string
from starlette import status

from src.api.app import create_api
from src.api.context import set_context, Context
from src.api.router import build_main_router
from src.utils.configs.app_config import AppConfiguration, ConfigManager
from src.utils.enums import EnvType

if TYPE_CHECKING:
    from fastapi import FastAPI


@pytest.fixture(scope="module")
def app() -> "FastAPI":
    return create_api()


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def context(app: "FastAPI", app_config: AppConfiguration, monkeymodule):
    context = await Context.instance(config=app_config, app=app)
    set_context(context, overwrite=True)
    await context.open()
    app.include_router(build_main_router(context))
    yield context
    await context.close()


@pytest.fixture(scope="module")
@pytest.mark.asyncio
async def api_client(context: "Context") -> AsyncClient:
    async with AsyncClient(app=context.app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def translated_words() -> dict[str, dict]:
    return {
        word: json.loads(
            (Path(__file__).parent / "data" / f"{word}.json").read_text()
        )
        for word in ("string", "challenge", "chance", "hello")
    }


@pytest.mark.asyncio
async def test_healthcheck(api_client: AsyncClient):
    response = await api_client.get(
        "/healthcheck"
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_unknown_word(api_client: AsyncClient):
    response = await api_client.post(
        "/api/v1/translations/delete", json={"word": random_string(10)}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "word", (
        "string",
        "challenge",
        "chance",
        "hello",
    )
)
async def test_translate(
        api_client: AsyncClient,
        translated_words: dict[str, dict],
        word: str
):
    response = await api_client.post(
        "/api/v1/translations/translate", json={"word": word, "to_lang": "ru"}
    )
    assert response.status_code == status.HTTP_200_OK
    data: dict = response.json()

    translated_words[word].pop("examples", None)
    data.pop("examples", None)
    error_msg = f"diff:\n{pformat(DeepDiff(translated_words[word], data, verbose_level=2))}"
    assert translated_words[word] == data, error_msg
