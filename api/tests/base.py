from fastapi import FastAPI
import pytest
from api.app import app
from httpx import AsyncClient


@pytest.fixture(scope="function")
def client() -> FastAPI:
    return AsyncClient(app)


@pytest.fixture
def anyio_backend():
    return 'asyncio'
