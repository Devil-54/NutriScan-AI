from __future__ import annotations

import io
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.v1.deps import get_storage_backend
from app.infrastructure.db import session as db_session_module
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import *  # noqa: F401,F403 - ensure all models are registered
from app.infrastructure.storage.storage_backend import LocalStorageBackend
from app.main import app
from app.middleware.rate_limit_middleware import limiter

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The slowapi limiter uses process-wide in-memory storage, which would
    otherwise leak request counts between test cases and cause spurious 429s."""
    limiter.reset()
    yield
    limiter.reset()


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine, tmp_path) -> AsyncGenerator[AsyncClient, None]:
    session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    # Route file storage to a per-test temp directory - never the real
    # storage/uploads directory - so tests are isolated and leave no residue.
    test_storage_backend = LocalStorageBackend(root_dir=str(tmp_path / "uploads"))

    def override_get_storage_backend():
        return test_storage_backend

    app.dependency_overrides[db_session_module.get_db] = override_get_db
    app.dependency_overrides[get_storage_backend] = override_get_storage_backend

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def make_test_image_bytes(width: int = 500, height: int = 500, fmt: str = "JPEG") -> bytes:
    buffer = io.BytesIO()
    img = Image.new("RGB", (width, height), color=(120, 180, 90))
    img.save(buffer, format=fmt)
    return buffer.getvalue()
