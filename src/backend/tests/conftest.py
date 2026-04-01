import asyncio
import pytest
import pytest_asyncio
from pathlib import Path
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from main import app  # noqa: E402
from core.config import settings  # noqa: E402
from database.db_helper import db_helper  # noqa: E402
from database.base import Base  # noqa: E402

TEST_DB_URL = str(settings.db.url_test)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    if "test" not in TEST_DB_URL:
        pytest.exit("ERROR: TEST_DB_URL must contain 'test'!")

    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    connection = await engine.connect()
    trans = await connection.begin()

    Session = async_sessionmaker(
        bind=connection, expire_on_commit=False, class_=AsyncSession
    )
    async_session = Session()

    yield async_session

    await async_session.close()
    await trans.rollback()
    await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession):
    async def override_get_session():
        yield session

    app.dependency_overrides[db_helper.dependency_session_getter] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
