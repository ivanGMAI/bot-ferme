from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from shared.exceptions.auth import AuthException
from utils.jwt_auth import create_access_token, create_refresh_token
from utils.security import hash_password, validate_password
from features.admins.schemas.schemas import AdminCreate, AdminLogin
from features.admins import crud
from features import Admin

async def register_admin(session: AsyncSession, admin_in: AdminCreate) -> Admin:
    """Регистрация нового админа с проверкой на дубликаты."""
    existing_admin: Admin | None = await crud.get_admin_by_username(session, admin_in.username)
    if existing_admin:
        raise AuthException(detail="Admin already exists")

    admin_data: dict = {
        "username": admin_in.username,
        "password": hash_password(admin_in.password),
    }
    return await crud.create_admin(session, admin_data)


async def login_admin(
    session: AsyncSession,
    admin_in: AdminLogin,
    response: Response
) -> dict[str, str]:
    """Аутентификация админа: проверка кредов и выдача JWT-пары в куки и JSON."""
    admin: Admin | None = await crud.get_admin_by_username(session, admin_in.username)

    if not admin or not validate_password(admin_in.password, admin.password):
        raise AuthException(detail="Invalid username or password")

    admin_id_str: str = str(admin.id)
    access_token: str = create_access_token(admin_id_str, admin.username)
    refresh_token: str = create_refresh_token(admin_id_str, admin.username)

    cookie_params: dict = {
        "httponly": True,
        "samesite": "lax",
        "secure": False,
    }

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.auth.access_token_lifetime_seconds,
        **cookie_params
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.auth.refresh_token_lifetime_seconds,
        **cookie_params
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }