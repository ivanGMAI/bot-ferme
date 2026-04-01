from uuid import UUID
from datetime import datetime, timedelta, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from features.users.models.users import User
from features.users.crud import (
    get_available_user,
    update_user_lock,
    create_user,
    reset_all_users_locks,
    get_all_users,
)
from features.users.schemas.schemas import UserCreate
from shared.exceptions import NotFoundException
from utils.security import hash_password


async def create_new_user(session: AsyncSession, user_in: UserCreate) -> User:
    """Хеширование пароля и создание нового пользователя."""
    user_data = user_in.model_dump()
    user_data["password"] = hash_password(user_data["password"])

    return await create_user(session, user_data)


async def lock_user_for_test(
    session: AsyncSession,
    project_id: UUID,
    env: str,
    domain: str,
    lock_duration: int | None = None,
) -> User:
    """Поиск и блокировка свободного пользователя под тест."""
    now = datetime.now(UTC)

    if lock_duration is not None:
        delta = timedelta(minutes=lock_duration)
    else:
        delta = timedelta(seconds=settings.auth.user_lock_timeout_seconds)

    threshold = now - delta

    user = await get_available_user(session, project_id, env, domain, threshold)

    if not user:
        raise NotFoundException(detail="No free users available")

    return await update_user_lock(session, user, now)


async def get_user_list(session: AsyncSession) -> list[User]:
    """Получение списка всех пользователей."""
    return await get_all_users(session)


async def release_all_users(session: AsyncSession) -> int:
    """Сброс блокировок для всех пользователей фермы."""
    return await reset_all_users_locks(session)
