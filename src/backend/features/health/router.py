from fastapi import APIRouter, status, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database.db_helper import db_helper

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/startup")
async def startup():
    """Проверка доступности ресурсов при старте приложения."""
    try:
        async with db_helper.session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "started"}
    except SQLAlchemyError:
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Service starting up: Database not ready",
        )


@router.get("/liveness")
async def liveness():
    """Проверка, что событийный цикл (Event Loop) не заблокирован."""
    return {"status": "ok"}


@router.get("/readiness")
async def readiness():
    """Проверка, что база данных на связи и готова к трафику."""
    try:
        async with db_helper.session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except SQLAlchemyError:
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Database is unreachable",
        )