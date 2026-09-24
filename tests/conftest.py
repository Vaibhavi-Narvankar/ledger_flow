import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database import get_db


def migrate_test_database() -> None:
    settings = get_settings()

    test_database_url = (
        settings.test_database_url
        .render_as_string(hide_password=False)
    )

    os.environ["ALEMBIC_DATABASE_URL"] = test_database_url

    try:
        alembic_config = Config("alembic.ini")
        command.upgrade(alembic_config, "head")
    finally:
        os.environ.pop("ALEMBIC_DATABASE_URL", None)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> None:
    migrate_test_database()


@pytest_asyncio.fixture
async def test_engine() -> AsyncEngine:
    settings = get_settings()

    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
        pool_pre_ping=True,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(
    test_engine: AsyncEngine,
) -> AsyncSession:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    from app.main import app

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as async_client:
            yield async_client
    finally:
        app.dependency_overrides.clear()