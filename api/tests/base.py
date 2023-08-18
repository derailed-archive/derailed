import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from api.app import app


@pytest.fixture(scope="function")
def client() -> FastAPI:
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def anyio_backend():
    return "asyncio"
