from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from features import Admin


async def get_admin_by_username(session: AsyncSession, username: str) -> Admin | None:
    """Поиск администратора в базе по уникальному юзернейму."""
    stmt = select(Admin).where(Admin.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create_admin(session: AsyncSession, admin_data: dict) -> Admin:
    """Создание записи нового администратора и сохранение в БД."""
    db_admin = Admin(**admin_data)
    session.add(db_admin)
    await session.commit()
    await session.refresh(db_admin)
    return db_admin