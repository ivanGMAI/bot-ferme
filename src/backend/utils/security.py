import bcrypt


def hash_password(password: str) -> str:
    """Хеширование пароля с использованием соли (bcrypt)."""
    password_bytes: bytes = password.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    """Проверка соответствия сырого пароля его хешу."""
    return bcrypt.checkpw(
        password=password.encode("utf-8"),
        hashed_password=hashed_password.encode("utf-8"),
    )