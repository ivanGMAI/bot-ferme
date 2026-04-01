import pytest
from features.admins import crud


@pytest.mark.asyncio
async def test_create_admin_direct(session):
    """Прямая проверка CRUD: создание админа в базе."""
    admin_data = {"username": "direct_admin", "password": "hashed_password_xyz"}

    new_admin = await crud.create_admin(session, admin_data)

    assert new_admin.username == "direct_admin"
    assert new_admin.id is not None
    assert new_admin.password == "hashed_password_xyz"


@pytest.mark.asyncio
async def test_get_admin_by_username(session):
    """Проверка поиска админа по юзернейму (и возврат None, если его нет)."""
    username = "search_me"
    admin_data = {"username": username, "password": "123"}
    await crud.create_admin(session, admin_data)

    admin = await crud.get_admin_by_username(session, username)
    assert admin is not None
    assert admin.username == username

    none_admin = await crud.get_admin_by_username(session, "ghost")
    assert none_admin is None
