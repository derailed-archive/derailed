import pytest
from httpx import AsyncClient
from api.models import User
from .utils import wait_for_token, set_token, token_context


@pytest.mark.anyio
async def test_create_user(client: AsyncClient) -> None:
    req = await client.post(
        '/register',
        json={
            'username': 'VincentRPS',
            'email': 'vincent@derailed.com',
            'password': 'Abcd12345'
        }
    )

    assert req.status_code == 201
    data: User = req.json()

    assert data['_token']
    assert data['username'] == 'VincentRPS'
    assert data['email'] == 'vincent@derailed.com'
    assert data.get('password') is None
    assert data['display_name'] is None
    assert data['flags'] == 8
    assert data['avatar'] is None
    assert data['bot'] is False

    set_token(data['_token'])


@pytest.mark.anyio
async def test_get_current_user(client: AsyncClient) -> None:
    await wait_for_token()

    r = await client.get(
        '/users/@me',
        headers={'Authorization': token_context.get()}
    )
    data: User = r.json()

    assert data['username'] == 'VincentRPS'
    assert data['email'] == 'vincent@derailed.com'
    assert data.get('password') is None
    assert data['display_name'] is None
    assert data['flags'] == 8
    assert data['avatar'] is None
    assert data['bot'] is False


@pytest.mark.anyio
async def test_delete_current_user(client: AsyncClient) -> None:
    await wait_for_token()

    r = await client.post(
        '/users/@me',
        json={'password': 'Abcd12345'},
        headers={'Authorization': token_context.get()}
    )

    assert r.status_code == 204
    assert r.content.decode() == ""
