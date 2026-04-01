import jwt
from datetime import datetime, timedelta
from pytz import utc
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from core.config import settings
from shared.exceptions.auth import InvalidTokenException


def encode_jwt(
    payload: dict,
    private_key: str | None = None,
    algorithm: str = settings.auth.algorithm,
) -> str:
    """Кодирование данных в JWT с использованием приватного ключа."""
    if private_key is None:
        private_key: str = settings.auth.private_key_path.read_text()
    return jwt.encode(payload, private_key, algorithm=algorithm)


def decode_jwt(
    token: str,
    public_key: str | None = None,
    algorithm: str = settings.auth.algorithm
) -> dict:
    """Декодирование JWT и проверка его валидности."""
    if public_key is None:
        public_key: str = settings.auth.public_key_path.read_text()
    try:
        return jwt.decode(token, public_key, algorithms=[algorithm])
    except ExpiredSignatureError:
        raise InvalidTokenException(detail="Token has expired")
    except InvalidTokenError:
        raise InvalidTokenException(detail="Invalid token signature or format")


def create_jwt_token(admin_id: str, username: str, lifetime_seconds: int) -> str:
    """Генерация структуры payload и создание токена."""
    current_time_utc: datetime = datetime.now(utc)
    expire: datetime = current_time_utc + timedelta(seconds=lifetime_seconds)
    payload: dict = {
        "sub": str(admin_id),
        "username": username,
        "exp": expire,
        "iat": current_time_utc,
    }
    return encode_jwt(payload)


def create_access_token(admin_id: str, username: str) -> str:
    """Создание краткосрочного Access токена."""
    return create_jwt_token(
        admin_id=admin_id,
        username=username,
        lifetime_seconds=settings.auth.access_token_lifetime_seconds,
    )


def create_refresh_token(admin_id: str, username: str) -> str:
    """Создание долгосрочного Refresh токена."""
    return create_jwt_token(
        admin_id=admin_id,
        username=username,
        lifetime_seconds=settings.auth.refresh_token_lifetime_seconds,
    )