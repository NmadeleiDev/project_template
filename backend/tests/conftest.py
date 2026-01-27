"""
Pytest configuration and shared fixtures.

This module provides reusable test fixtures for database sessions,
test clients, and test data factories.
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.app import app
from api.dependencies import get_session
from core.db import Base
from core.settings import postgres_settings


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create event loop for async tests.

    Session-scoped to reuse across all tests for better performance.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """
    Create async SQLAlchemy engine with in-memory SQLite for testing.

    Uses StaticPool to maintain single connection across async operations.
    Database is recreated for each test function to ensure isolation.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create async database session for testing.

    Provides clean database session for each test function.
    Automatically rolls back after test completion.
    """
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def sync_engine():
    """
    Create sync SQLAlchemy engine for synchronous tests.

    Useful for testing migrations or sync database operations.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def sync_session(sync_engine) -> Generator[Session, None, None]:
    """
    Create sync database session for testing.

    Provides clean database session for synchronous tests.
    """
    session_maker = sessionmaker(bind=sync_engine)
    session = session_maker()
    yield session
    session.rollback()
    session.close()


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create async HTTP test client for FastAPI application.

    Overrides database session dependency to use test database.
    Use this fixture for testing API endpoints.

    Example:
        async def test_health_check(client):
            response = await client.get("/api/health")
            assert response.status_code == 200
    """

    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def test_user(async_session: AsyncSession):
    """
    Create test user in database.

    Returns:
        User model instance with:
        - email: test@example.com
        - password: TestPassword123!

    Example:
        async def test_with_user(test_user):
            assert test_user.email == "test@example.com"
    """
    from repository.models import User
    from service.security import get_password_hash

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(
    client: AsyncClient, test_user
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create authenticated HTTP client with valid JWT token.

    Creates test user and authenticates client automatically.
    Use for testing protected endpoints.

    Example:
        async def test_protected_route(authenticated_client):
            response = await authenticated_client.get("/api/user/me")
            assert response.status_code == 200
    """
    # Login to get JWT token
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200

    # Client now has JWT cookie set
    yield client


# ============================================================================
# UTILITY FIXTURES
# ============================================================================


@pytest.fixture
def mock_redis(monkeypatch):
    """
    Mock Redis connection for testing.

    Prevents tests from requiring actual Redis instance.
    Useful for testing task queue functionality.
    """
    # TODO: Implement Redis mock when testing taskiq tasks
    pass


@pytest.fixture
def mock_sentry(monkeypatch):
    """
    Mock Sentry client to prevent error reporting during tests.
    """
    monkeypatch.setenv("SENTRY_ENABLED", "false")
