import pytest
import uuid
from httpx import AsyncClient
from utils.jwt_auth import create_access_token, encode_jwt


@pytest.mark.asyncio
async def test_admin_get_me_success(client: AsyncClient):
    """Проверка получения инфо о себе после реги и логина."""
    admin_data = {"username": "auth_boss", "password": "securepassword123"}
    await client.post("/api/v1/admins/register", json=admin_data)
    await client.post("/api/v1/admins/login", json=admin_data)

    response = await client.get("/api/v1/admins/me")
    assert response.status_code == 200
    assert response.json()["username"] == "auth_boss"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """Проверка, что без токена в /me не пускает (401)."""
    response = await client.get("/api/v1/admins/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_not_found(client: AsyncClient):
    """Ошибка 401, если в токене валидный UUID, но админа нет в базе."""
    fake_id = str(uuid.uuid4())
    token = create_access_token(admin_id=fake_id, username="ghost")
    client.cookies.set("access_token", token)

    response = await client.get("/api/v1/admins/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_admin_invalid_payload(client: AsyncClient):
    """Ошибка 401, если в JWT отсутствует обязательное поле 'sub'."""
    token = encode_jwt({"some_data": "no_sub_here"})
    client.cookies.set("access_token", token)

    response = await client.get("/api/v1/admins/me")
    assert response.status_code == 401
    assert "payload is invalid" in response.json()["detail"]
