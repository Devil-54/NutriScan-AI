from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.infrastructure.db.models.user import User
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.user_repository import UserRepository

pytestmark = pytest.mark.asyncio


class TestUserRepository:
    async def test_get_by_email_case_insensitive_lookup(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        user = User(name="Jane", email="jane@example.com", password_hash=hash_password("StrongPass1"))
        repo.add(user)
        await db_session.commit()

        found = await repo.get_by_email("jane@example.com")
        assert found is not None
        assert found.email == "jane@example.com"

    async def test_email_exists(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        assert await repo.email_exists("nobody@example.com") is False

        user = User(name="Jane", email="jane@example.com", password_hash=hash_password("StrongPass1"))
        repo.add(user)
        await db_session.commit()

        assert await repo.email_exists("jane@example.com") is True


class TestAuditLogRepository:
    async def test_record_creates_audit_entry(self, db_session: AsyncSession) -> None:
        user_repo = UserRepository(db_session)
        audit_repo = AuditLogRepository(db_session)

        user = User(name="Jane", email="jane@example.com", password_hash=hash_password("StrongPass1"))
        user_repo.add(user)
        await db_session.flush()

        log = await audit_repo.record(action="TEST_ACTION", user_id=user.user_id, metadata={"key": "value"})
        await db_session.commit()

        assert log.action == "TEST_ACTION"
        assert log.user_id == user.user_id
        assert log.log_metadata == {"key": "value"}
