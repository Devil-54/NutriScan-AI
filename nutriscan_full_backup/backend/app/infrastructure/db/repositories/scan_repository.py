from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.domain.enums import ScanStatus
from app.infrastructure.db.models.scan_session import ScanSession
from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.repositories.base_repository import BaseRepository


class ScanRepository(BaseRepository[ScanSession]):
    model = ScanSession

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_owned_by_id(
        self, scan_id: uuid.UUID, user_id: uuid.UUID, include_deleted: bool = False
    ) -> ScanSession | None:
        stmt = (
            select(ScanSession)
            .options(joinedload(ScanSession.personalized_evaluation), joinedload(ScanSession.ocr_result))
            .where(ScanSession.scan_id == scan_id, ScanSession.user_id == user_id)
        )
        if not include_deleted:
            stmt = stmt.where(ScanSession.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_active_duplicate(self, user_id: uuid.UUID, checksum_sha256: str) -> ScanSession | None:
        """Duplicate protection: same user, same file content, not deleted."""
        stmt = select(ScanSession).where(
            ScanSession.user_id == user_id,
            ScanSession.checksum_sha256 == checksum_sha256,
            ScanSession.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def count_uploads_since(self, user_id: uuid.UUID, since: datetime) -> int:
        stmt = select(func.count()).select_from(ScanSession).where(
            ScanSession.user_id == user_id, ScanSession.created_at >= since
        )
        return (await self.session.execute(stmt)).scalar_one()

    async def list_history(
        self,
        user_id: uuid.UUID,
        page: int,
        limit: int,
        status: ScanStatus | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        include_deleted: bool = False,
    ) -> tuple[list[ScanSession], int]:
        conditions = [ScanSession.user_id == user_id]
        if not include_deleted:
            conditions.append(ScanSession.deleted_at.is_(None))
        if status is not None:
            conditions.append(ScanSession.status == status)
        if search:
            pattern = f"%{search}%"
            conditions.append(or_(ScanSession.original_filename.ilike(pattern), ScanSession.notes.ilike(pattern)))

        base_stmt = select(ScanSession).options(
            joinedload(ScanSession.personalized_evaluation),
            joinedload(ScanSession.ocr_result),
        ).where(and_(*conditions))
        count_stmt = select(func.count()).select_from(ScanSession).where(and_(*conditions))

        sort_column = {
            "created_at": ScanSession.created_at,
            "updated_at": ScanSession.updated_at,
            "status": ScanSession.status,
            "file_size_bytes": ScanSession.file_size_bytes,
        }.get(sort_by, ScanSession.created_at)
        base_stmt = base_stmt.order_by(sort_column.desc() if sort_dir == "desc" else sort_column.asc())
        base_stmt = base_stmt.offset((page - 1) * limit).limit(limit)

        total = (await self.session.execute(count_stmt)).scalar_one()
        rows = (await self.session.execute(base_stmt)).scalars().all()
        return list(rows), total

    async def history_stats(self, user_id: uuid.UUID) -> tuple[int, int, int]:
        """Return persisted scan totals without loading or recalculating reports.

        The evaluation join is constrained by scan ID, so each saved scan is
        counted once and no evaluation from another user can contribute.
        """
        stmt = select(
            func.count(ScanSession.scan_id),
            func.coalesce(func.sum(case((MedicalEvaluation.status == "safe", 1), else_=0)), 0),
            func.coalesce(func.sum(case((MedicalEvaluation.status == "warning", 1), else_=0)), 0),
        ).select_from(ScanSession).outerjoin(
            MedicalEvaluation,
            and_(
                MedicalEvaluation.scan_id == ScanSession.scan_id,
                MedicalEvaluation.user_id == ScanSession.user_id,
            ),
        ).where(
            ScanSession.user_id == user_id,
            ScanSession.deleted_at.is_(None),
        )
        total, safe, warnings = (await self.session.execute(stmt)).one()
        return int(total), int(safe), int(warnings)

    async def soft_delete(self, scan: ScanSession) -> None:
        scan.deleted_at = datetime.now(timezone.utc)
        await self.flush()

    async def restore(self, scan: ScanSession) -> None:
        scan.deleted_at = None
        await self.flush()

    async def find_expired(self, as_of: datetime | None = None) -> list[ScanSession]:
        """
        Two distinct expiry paths, matching the two config knobs:
        - Active scans past `expires_at` (SCAN_EXPIRATION_DAYS from upload) that were never deleted.
        - Soft-deleted scans whose `deleted_at` is older than DELETED_SCAN_RETENTION_DAYS -
          past this point a restore is no longer offered, so the files can be purged for good.
        """
        now = as_of or datetime.now(timezone.utc)
        retention_cutoff = now - timedelta(days=settings.DELETED_SCAN_RETENTION_DAYS)

        stmt = select(ScanSession).where(
            ScanSession.storage_path.is_not(None),
            or_(
                and_(ScanSession.expires_at.is_not(None), ScanSession.expires_at <= now, ScanSession.deleted_at.is_(None)),
                and_(ScanSession.deleted_at.is_not(None), ScanSession.deleted_at <= retention_cutoff),
            ),
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def all_storage_paths(self) -> set[str]:
        """Every storage_path/thumbnail_path currently referenced by a DB row - used by orphan-file detection."""
        stmt = select(ScanSession.storage_path, ScanSession.thumbnail_path)
        rows = (await self.session.execute(stmt)).all()
        paths: set[str] = set()
        for storage_path, thumbnail_path in rows:
            paths.add(storage_path)
            if thumbnail_path:
                paths.add(thumbnail_path)
        return paths
