from typing import AsyncGenerator, Generator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from core.settings import postgres_settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine
from contextlib import contextmanager

async_engine = create_async_engine(postgres_settings.async_app_database_url, echo=False)
sync_engine = create_engine(postgres_settings.sync_app_database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_db(
    commit_on_close: bool = True, rollback_on_error: bool = True
) -> AsyncGenerator[AsyncSession, None]:
    """Async database session generator with configurable commit/rollback behavior"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            if commit_on_close:
                await session.commit()
        except Exception as e:
            if rollback_on_error:
                await session.rollback()
            raise e


async def get_async_db_for_router() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async database sessions"""
    async for session in get_async_db():
        yield session


fastapi_db_dep = Depends(get_async_db_for_router)


@contextmanager
def sync_db_session(commit_on_close: bool = True, rollback_on_error: bool = True):
    """Context manager for sync database sessions (useful for Taskiq tasks)"""
    session = SessionLocal()
    try:
        yield session
        if commit_on_close:
            session.commit()
    except Exception as e:
        if rollback_on_error:
            session.rollback()
        raise e
    finally:
        session.close()
