from fastapi import FastAPI
import pytest
from api.app import app
from httpx import AsyncClient


@pytest.fixture(scope="function")
def client() -> FastAPI:
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def anyio_backend():
    return 'asyncio'
