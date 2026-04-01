import pytest
from uuid import uuid4
from datetime import datetime, timedelta, UTC
from features.users.services import lock_user_for_test, create_new_user
from features.users.schemas.schemas import UserCreate
from features.users.schemas.enums import Environment, UserDomain
from shared.exceptions import NotFoundException


@pytest.mark.asyncio
async def test_lock_available_user_success(session):
    """Успешный захват свободного пользователя."""
    project_id = uuid4()
    user_in = UserCreate(
        login="test_bot_1@example.com",
        password="secret_password",
        project_id=project_id,
        env=Environment.PROD,
        domain=UserDomain.REGULAR,
    )
    await create_new_user(session, user_in)

    locked = await lock_user_for_test(
        session=session,
        project_id=project_id,
        env=Environment.PROD,
        domain=UserDomain.REGULAR,
    )

    assert locked.login == "test_bot_1@example.com"
    assert locked.locktime is not None
    assert (datetime.now(UTC) - locked.locktime).total_seconds() < 2


@pytest.mark.asyncio
async def test_lock_expired_user_success(session):
    """Захват пользователя с истекшим таймаутом блокировки."""
    project_id = uuid4()
    old_lock = datetime.now(UTC) - timedelta(minutes=20)

    user_in = UserCreate(
        login="expired_bot@example.com",
        password="secret_password",
        project_id=project_id,
        env=Environment.STAGE,
        domain=UserDomain.CANARY,
    )
    user = await create_new_user(session, user_in)

    user.locktime = old_lock
    await session.commit()

    locked = await lock_user_for_test(
        session=session,
        project_id=project_id,
        env=Environment.STAGE,
        domain=UserDomain.CANARY,
    )

    assert locked.login == "expired_bot@example.com"
    assert locked.locktime > old_lock


@pytest.mark.asyncio
async def test_lock_user_no_available(session):
    """Ошибка при отсутствии свободных пользователей."""
    project_id = uuid4()

    user_in = UserCreate(
        login="busy_bot@example.com",
        password="secret_password",
        project_id=project_id,
        env=Environment.PROD,
        domain=UserDomain.REGULAR,
    )
    user = await create_new_user(session, user_in)

    user.locktime = datetime.now(UTC)
    await session.commit()

    with pytest.raises(NotFoundException):
        await lock_user_for_test(
            session=session,
            project_id=project_id,
            env=Environment.PROD,
            domain=UserDomain.REGULAR,
            lock_duration=10,
        )
