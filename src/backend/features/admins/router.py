from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from features import Admin
from database.db_helper import db_helper
from features.admins.dependencies.auth import get_current_admin
from features.admins.schemas import schemas
from features.admins.services import register_admin, login_admin

router = APIRouter(prefix="/admins", tags=["Admins Auth"])


@router.post("/register", response_model=schemas.AdminRead)
async def register(
    admin_in: schemas.AdminCreate,
    session: AsyncSession = Depends(db_helper.dependency_session_getter),
) -> Admin:
    """Регистрация нового администратора в системе."""
    return await register_admin(session=session, admin_in=admin_in)


@router.post("/login")
async def login(
    response: Response,
    admin_in: schemas.AdminLogin,
    session: AsyncSession = Depends(db_helper.dependency_session_getter),
) -> dict[str, str]:
    """Вход в систему: проверка пароля и установка сессионных JWT-кук."""
    return await login_admin(session=session, admin_in=admin_in, response=response)


@router.get("/me", response_model=schemas.AdminRead)
async def get_my_profile(admin: Admin = Depends(get_current_admin)) -> Admin:
    """Получение данных текущего авторизованного администратора."""
    return admin