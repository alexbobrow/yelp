import asyncio
from contextlib import asynccontextmanager
from typing import Generator

import asyncpg
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.containers import Container
from config.settings import Settings
from config.utils import assemble_dsn
from main import app


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> Generator[None, None, None]:
    asyncio.run(_recreate_test_database())
    _run_alembic_migrations()
    yield


async def _recreate_test_database() -> None:
    settings = Settings()
    admin_dsn = assemble_dsn(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database="postgres",
        is_async=False,
    )
    conn = await asyncpg.connect(dsn=admin_dsn)
    await conn.execute(f'DROP DATABASE IF EXISTS "{settings.db_name}" WITH (FORCE)')
    await conn.execute(f'CREATE DATABASE "{settings.db_name}"')
    await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    await conn.close()

    test_dsn = assemble_dsn(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        is_async=False,
    )
    conn = await asyncpg.connect(test_dsn)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    await conn.close()


def _run_alembic_migrations() -> None:
    settings = Settings()
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.db_dsn)
    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncSession:
    settings = Settings()
    test_engine = create_async_engine(settings.db_dsn, future=True)
    async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_engine.connect() as conn:
        trans = await conn.begin()
        async with async_session(bind=conn, expire_on_commit=False) as session:
            yield session
        await trans.rollback()


@pytest.fixture(scope="function")
def container(db: AsyncSession) -> Generator[Container, None, None]:
    container = Container()

    class TestDbManager:
        @asynccontextmanager
        async def session(self) -> AsyncSession:
            yield db

    container.db.override(TestDbManager())
    yield container
    container.unwire()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    settings = app.container.settings()
    api_key = settings.api_key
    headers = {"Authorization": f"Token {api_key}"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as ac:
        yield ac


@pytest_asyncio.fixture
async def guest_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
