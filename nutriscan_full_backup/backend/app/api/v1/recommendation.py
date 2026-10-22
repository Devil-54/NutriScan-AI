from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import (
    CurrentUserDep,
    get_health_profile_repository,
    get_medical_evaluation_repository,
    get_product_evaluation_service,
    get_recommendation_engine,
    get_scan_repository,
)
from app.domain.schemas.common import PaginatedResponse, SuccessResponse
from app.domain.schemas.recommendation import RecommendationHistoryItem, RecommendationRequest, RecommendationResponse
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.medical_rules.evaluation_service import ProductEvaluationService
from app.infrastructure.recommendation.engine import RecommendationEngine
from app.use_cases.recommendation.generate_recommendation import GenerateRecommendationUseCase
from app.use_cases.recommendation.get_recommendation_history import GetRecommendationHistoryUseCase

router = APIRouter(prefix="/recommendation", tags=["Recommendation Engine"])


@router.post("/generate", response_model=SuccessResponse[RecommendationResponse])
async def generate_recommendation(
    payload: RecommendationRequest,
    current_user: CurrentUserDep,
    evaluation_service: Annotated[ProductEvaluationService, Depends(get_product_evaluation_service)],
    recommendation_engine: Annotated[RecommendationEngine, Depends(get_recommendation_engine)],
    health_profile_repo: Annotated[HealthProfileRepository, Depends(get_health_profile_repository)],
    evaluation_repo: Annotated[MedicalEvaluationRepository, Depends(get_medical_evaluation_repository)],
    scan_repo: Annotated[ScanRepository, Depends(get_scan_repository)],
) -> SuccessResponse[RecommendationResponse]:
    use_case = GenerateRecommendationUseCase(
        evaluation_service, recommendation_engine, health_profile_repo, evaluation_repo, scan_repo
    )
    result = await use_case.execute(current_user.user_id, payload)
    return SuccessResponse(data=result)


@router.get("/history", response_model=PaginatedResponse[RecommendationHistoryItem])
async def get_recommendation_history(
    current_user: CurrentUserDep,
    evaluation_repo: Annotated[MedicalEvaluationRepository, Depends(get_medical_evaluation_repository)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[RecommendationHistoryItem]:
    use_case = GetRecommendationHistoryUseCase(evaluation_repo)
    items, meta = await use_case.execute(current_user.user_id, page, limit)
    return PaginatedResponse(data=items, meta=meta)
