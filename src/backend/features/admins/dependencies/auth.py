from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_helper import db_helper
from utils.jwt_auth import decode_jwt
from shared.exceptions.auth import AuthException, UserNotFoundAuthException
from features import Admin


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """Кастомный провайдер OAuth2, умеющий искать токен не только в Header, но и в Cookie."""
    async def __call__(self, request: Request) -> str | None:
        token = request.cookies.get("access_token")
        if token:
            return token
        return await super().__call__(request)


oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="/api/admins/login", auto_error=False
)


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.dependency_session_getter),
) -> Admin:
    """Зависимость для извлечения текущего админа из JWT-токена и базы данных."""
    if not token:
        raise AuthException(detail="Not authenticated")

    payload = decode_jwt(token)
    admin_id: str = payload.get("sub")

    if not admin_id:
        raise AuthException(detail="Token payload is invalid")

    admin = await session.get(Admin, admin_id)
    if not admin:
        raise UserNotFoundAuthException()
    return admin