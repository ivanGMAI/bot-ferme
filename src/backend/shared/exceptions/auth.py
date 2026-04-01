from http import HTTPStatus
from shared.exceptions import AppException


class AuthException(AppException):
    status_code: int = HTTPStatus.UNAUTHORIZED
    detail: str = "Could not validate credentials"


class InvalidTokenException(AuthException):
    detail: str = "Token is invalid or expired"


class UserNotFoundAuthException(AuthException):
    detail: str = "Admin user from token not found"
