import pytest
from datetime import datetime, timedelta, UTC
from utils.security import hash_password, validate_password
from utils.jwt_auth import encode_jwt, decode_jwt, create_access_token
from shared.exceptions.auth import InvalidTokenException


def test_password_hashing():
    """Тест хеширования и проверки пароля."""
    pwd = "secret_password_123"
    hashed = hash_password(pwd)

    assert hashed != pwd
    assert validate_password(pwd, hashed) is True
    assert validate_password("wrong_password", hashed) is False


def test_jwt_encode_decode_success():
    """Тест успешного создания и декодирования JWT."""
    payload = {"sub": "123", "user": "test"}
    token = encode_jwt(payload)
    decoded = decode_jwt(token)

    assert decoded["sub"] == "123"
    assert decoded["user"] == "test"


def test_jwt_expired_token():
    """Тест ошибки при истекшем токене (закрывает блок ExpiredSignatureError)."""
    # Создаем нагрузку, которая уже истекла
    payload = {"sub": "123", "exp": datetime.now(UTC) - timedelta(minutes=1)}
    token = encode_jwt(payload)

    with pytest.raises(InvalidTokenException) as exc:
        decode_jwt(token)
    assert "Token has expired" in str(exc.value.detail)


def test_jwt_invalid_format():
    """Тест ошибки при неверном формате/подписи (закрывает блок InvalidTokenError)."""
    with pytest.raises(InvalidTokenException) as exc:
        decode_jwt("not.a.valid.token")
    assert "Invalid token signature or format" in str(exc.value.detail)


def test_create_access_token_structure():
    """Тест структуры создаваемого access токена."""
    admin_id = "test-uuid"
    username = "admin"
    token = create_access_token(admin_id, username)
    decoded = decode_jwt(token)

    assert decoded["sub"] == admin_id
    assert decoded["username"] == username
    assert "exp" in decoded
    assert "iat" in decoded
