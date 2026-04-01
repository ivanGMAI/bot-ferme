from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from features.admins.dependencies.auth import get_current_admin
from features.users.schemas.schemas import UserRead, UserLockRequest, UserCreate
from features.users.services import (
    lock_user_for_test,
    create_new_user,
    get_user_list,
    release_all_users,
)

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(get_current_admin)]
)


@router.get("/", response_model=list[UserRead])
async def get_users(db: AsyncSession = Depends(db_helper.dependency_session_getter)):
    """Получить список всех существующих пользователей ботофермы."""
    return await get_user_list(db)


@router.post("/", response_model=UserRead)
async def create_user(
    payload: UserCreate, db: AsyncSession = Depends(db_helper.dependency_session_getter)
):
    """Создать нового пользователя в ботоферме."""
    return await create_new_user(db, payload)


@router.post("/lock", response_model=UserRead)
async def lock_user(
    payload: UserLockRequest,
    db: AsyncSession = Depends(db_helper.dependency_session_getter),
):
    """Заблокировать и получить свободного пользователя для E2E-теста."""
    return await lock_user_for_test(
        session=db,
        project_id=payload.project_id,
        env=payload.env,
        domain=payload.domain,
    )


@router.post("/free-all")
async def free_users(db: AsyncSession = Depends(db_helper.dependency_session_getter)):
    """Снять блокировки со всех пользователей в системе."""
    count = await release_all_users(db)
    return {"message": f"Successfully released {count} users"}
