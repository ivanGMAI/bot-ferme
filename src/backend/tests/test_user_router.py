import pytest
from httpx import AsyncClient
from uuid import uuid4
from features.users.schemas.enums import Environment, UserDomain


@pytest.fixture
async def authenticated_client(client: AsyncClient):
    admin_data = {"username": "test_boss", "password": "password123"}
    await client.post("/api/v1/admins/register", json=admin_data)
    await client.post("/api/v1/admins/login", json=admin_data)
    return client


@pytest.mark.asyncio
async def test_create_user_success(authenticated_client: AsyncClient):
    payload = {
        "login": f"bot_{uuid4()}@test.com",
        "password": "hashed_pass",
        "project_id": str(uuid4()),
        "env": Environment.PROD.value,
        "domain": UserDomain.REGULAR.value,
    }
    response = await authenticated_client.post("/api/v1/users/", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_users_list(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_free_all_users_endpoint(authenticated_client: AsyncClient):
    response = await authenticated_client.post("/api/v1/users/free-all")
    assert response.status_code == 200
    assert "Successfully released" in response.json()["message"]
