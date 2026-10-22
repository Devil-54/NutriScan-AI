from __future__ import annotations

import uuid

from app.domain.schemas.common import PaginationMeta
from app.domain.schemas.recommendation import RecommendationHistoryItem
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository


class GetRecommendationHistoryUseCase:
    def __init__(self, evaluation_repo: MedicalEvaluationRepository) -> None:
        self.evaluation_repo = evaluation_repo

    async def execute(
        self, user_id: uuid.UUID, page: int, limit: int
    ) -> tuple[list[RecommendationHistoryItem], PaginationMeta]:
        rows, total = await self.evaluation_repo.list_for_user(user_id, page, limit)
        total_pages = (total + limit - 1) // limit if total else 0
        items = [
            RecommendationHistoryItem(
                evaluation_id=r.evaluation_id,
                status=r.status,
                recommendation_score=r.health_score,
                confidence_score=r.confidence_score,
                unsafe_foods=r.unsafe_ingredients,
                created_at=r.created_at,
            )
            for r in rows
        ]
        return items, PaginationMeta(page=page, limit=limit, total=total, total_pages=total_pages)
