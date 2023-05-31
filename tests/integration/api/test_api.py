from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient
from starlette import status

from src.api.app import create_api
from src.api.context import set_context
from src.api.router import build_main_router
from src.utils.configs.app_config import AppConfiguration, ConfigManager
from src.utils.enums import EnvType

if TYPE_CHECKING:
    from fastapi import FastAPI


@pytest.fixture(scope="module")
def app() -> "FastAPI":
    return create_api()


@pytest.fixture(scope="module")
async def context(app: "FastAPI", monkeymodule):
    env_type = EnvType.TEST
    monkeymodule.setenv("ENV", env_type.value)
    app_config: AppConfiguration = ConfigManager.load_configuration(env=env_type)
    from src.api.context import Context
    context = await Context.instance(config=app_config)
    set_context(context, overwrite=True)
    await context.open()
    app.include_router(build_main_router(context))
    yield context
    await context.close()


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def api_client(app: "FastAPI") -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_healthcheck(api_client: AsyncClient):
    response = await api_client.get(
        "/healthcheck"
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_healthcheck__(api_client: AsyncClient):
    print("")
    assert True is True
