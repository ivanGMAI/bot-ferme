import pytest
from fastapi import Response
from features.admins.services import register_admin, login_admin
from features.admins.schemas.schemas import AdminCreate, AdminLogin
from shared.exceptions.auth import AuthException


@pytest.mark.asyncio
async def test_register_admin_success(session):
    """Успешная регистрация нового админа."""
    admin_in = AdminCreate(username="admin_test", password="super_password_123")
    new_admin = await register_admin(session, admin_in)

    assert new_admin.username == "admin_test"
    assert hasattr(new_admin, "id")


@pytest.mark.asyncio
async def test_register_admin_duplicate_error(session):
    """Ошибка при регистрации существующего админа."""
    admin_in = AdminCreate(username="unique_admin", password="password123")
    await register_admin(session, admin_in)

    with pytest.raises(AuthException) as exc:
        await register_admin(session, admin_in)
    assert "Admin already exists" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_login_admin_success(session):
    """Успешный вход и установка кук."""
    username = "login_test"
    password = "password123"
    await register_admin(session, AdminCreate(username=username, password=password))

    response = Response()
    login_data = AdminLogin(username=username, password=password)

    result = await login_admin(session, login_data, response)

    assert "access_token" in result
    assert result["token_type"] == "bearer"

    cookies = response.headers.getlist("set-cookie")

    all_cookies_str = "".join(cookies)

    assert "access_token" in all_cookies_str
    assert "refresh_token" in all_cookies_str


@pytest.mark.asyncio
async def test_login_admin_invalid_password(session):
    """Ошибка при неверном пароле."""
    username = "wrong_pass_user"
    await register_admin(
        session, AdminCreate(username=username, password="correct_password")
    )

    response = Response()
    login_data = AdminLogin(username=username, password="wrong_password")

    with pytest.raises(AuthException) as exc:
        await login_admin(session, login_data, response)
    assert "Invalid username or password" in str(exc.value.detail)
