from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.repositories.base_repository import BaseRepository


class MedicalEvaluationRepository(BaseRepository[MedicalEvaluation]):
    model = MedicalEvaluation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_user(self, user_id: uuid.UUID, page: int, limit: int) -> tuple[list[MedicalEvaluation], int]:
        count_stmt = select(func.count()).select_from(MedicalEvaluation).where(MedicalEvaluation.user_id == user_id)
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = (
            select(MedicalEvaluation)
            .where(MedicalEvaluation.user_id == user_id)
            .order_by(MedicalEvaluation.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total
