from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from features import User
from shared.exceptions import RuleException


async def get_user_by_login(session: AsyncSession, login: str) -> User | None:
    """Поиск пользователя по логину."""
    stmt = select(User).where(User.login == login)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: dict) -> User:
    """Проверка уникальности и создание нового пользователя."""
    existing_user = await get_user_by_login(session, user_data["login"])
    if existing_user:
        raise RuleException(detail=f"User {user_data['login']} already exists")

    new_user = User(**user_data)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def get_available_user(
    session: AsyncSession,
    project_id: UUID,
    env: str,
    domain: str,
    expiration_threshold: datetime,
) -> User | None:
    """Поиск одного свободного пользователя с учетом таймаута блокировки."""
    stmt = (
        select(User)
        .where(
            and_(
                User.project_id == project_id,
                User.env == env,
                User.domain == domain,
                or_(User.locktime.is_(None), User.locktime < expiration_threshold),
            )
        )
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def update_user_lock(
    session: AsyncSession, user: User, lock_time: datetime
) -> User:
    """Обновление времени блокировки пользователя."""
    user.locktime = lock_time
    await session.commit()
    return user


async def get_all_users(session: AsyncSession) -> list[User]:
    """Получение всех пользователей, отсортированных по дате создания."""
    stmt = select(User).order_by(User.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def reset_all_users_locks(session: AsyncSession) -> int:
    """Сброс всех блокировок (установка locktime в None)."""
    stmt = update(User).values(locktime=None)
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount
