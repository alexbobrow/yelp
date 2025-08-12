from asyncio import current_task
from contextlib import asynccontextmanager

from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


class DbManager:
    def __init__(self, settings: BaseSettings):
        self.settings = settings
        self.engine = create_async_engine(settings.db_dsn, echo=True)
        self.session_factory = async_scoped_session(
            async_sessionmaker(
                self.engine,
                expire_on_commit=False,
                autoflush=False,
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        session = self.session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
