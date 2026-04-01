import pytest
from uuid import uuid4
from datetime import datetime, timedelta, UTC
from features.users import crud
from features.users.schemas.enums import Environment, UserDomain
from shared.exceptions import RuleException


@pytest.mark.asyncio
async def test_create_and_get_user(session):
    """Проверка создания юзера и его поиска по логину в базе."""
    user_data = {
        "login": "unique_bot@test.com",
        "project_id": uuid4(),
        "env": Environment.PROD,
        "domain": UserDomain.REGULAR,
        "password": "hashed_password_123",
    }

    new_user = await crud.create_user(session, user_data)
    assert new_user.login == user_data["login"]

    found_user = await crud.get_user_by_login(session, user_data["login"])
    assert found_user.id == new_user.id


@pytest.mark.asyncio
async def test_create_user_duplicate_raises(session):
    """Проверка RuleException при попытке создать дубликат юзера."""
    user_data = {
        "login": "double@test.com",
        "project_id": uuid4(),
        "env": Environment.PROD,
        "domain": UserDomain.REGULAR,
        "password": "123",
    }
    await crud.create_user(session, user_data)

    with pytest.raises(RuleException) as exc:
        await crud.create_user(session, user_data)
    assert "already exists" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_get_available_user_logic(session):
    """Проверка поиска свободного юзера, у которого протух locktime."""
    project_id = uuid4()
    env = Environment.PROD
    domain = UserDomain.REGULAR

    old_time = datetime.now(UTC) - timedelta(hours=1)
    user_data = {
        "login": "expired_lock@test.com",
        "project_id": project_id,
        "env": env,
        "domain": domain,
        "password": "123",
        "locktime": old_time,
    }
    await crud.create_user(session, user_data)

    threshold = datetime.now(UTC) - timedelta(minutes=10)

    user = await crud.get_available_user(session, project_id, env, domain, threshold)
    assert user is not None
    assert user.login == "expired_lock@test.com"


@pytest.mark.asyncio
async def test_reset_all_locks(session):
    """Проверка массового сброса всех локов у юзеров в None."""
    user_data = {
        "login": "locked_guy@test.com",
        "project_id": uuid4(),
        "env": Environment.PROD,
        "domain": UserDomain.REGULAR,
        "password": "123",
        "locktime": datetime.now(UTC),
    }
    await crud.create_user(session, user_data)

    count = await crud.reset_all_users_locks(session)
    assert count >= 1

    all_users = await crud.get_all_users(session)
    for u in all_users:
        assert u.locktime is None
