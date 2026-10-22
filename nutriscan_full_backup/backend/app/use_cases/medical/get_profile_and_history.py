from __future__ import annotations

import uuid

from app.domain.schemas.common import PaginationMeta
from app.domain.schemas.medical import EvaluationHistoryItem, MedicalProfileSummary
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder


class GetMedicalProfileUseCase:
    def __init__(self, context_builder: MedicalContextBuilder) -> None:
        self.context_builder = context_builder

    async def execute(self, user_id: uuid.UUID) -> MedicalProfileSummary:
        summary = await self.context_builder.build_profile_summary(user_id)
        return MedicalProfileSummary(**summary)


class GetEvaluationHistoryUseCase:
    def __init__(self, evaluation_repo: MedicalEvaluationRepository) -> None:
        self.evaluation_repo = evaluation_repo

    async def execute(self, user_id: uuid.UUID, page: int, limit: int) -> tuple[list[EvaluationHistoryItem], PaginationMeta]:
        rows, total = await self.evaluation_repo.list_for_user(user_id, page, limit)
        total_pages = (total + limit - 1) // limit if total else 0
        items = [EvaluationHistoryItem.model_validate(r, from_attributes=True) for r in rows]
        return items, PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages)
