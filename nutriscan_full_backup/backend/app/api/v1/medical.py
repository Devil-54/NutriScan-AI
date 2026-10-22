from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.deps import (
    CurrentUserDep,
    get_allergen_repository,
    get_ingredient_repository,
    get_medical_context_builder,
    get_medical_evaluation_repository,
    get_nutrition_repository,
    get_rule_engine,
)
from app.domain.schemas.common import PaginatedResponse, SuccessResponse
from app.domain.schemas.medical import EvaluateRequest, EvaluateResponse, EvaluationHistoryItem, MedicalProfileSummary
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.nutrition_repository import NutritionRepository
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder
from app.infrastructure.medical_rules.engine import RuleEngine
from app.use_cases.medical.evaluate_product import EvaluateProductUseCase
from app.use_cases.medical.get_profile_and_history import GetEvaluationHistoryUseCase, GetMedicalProfileUseCase

router = APIRouter(prefix="/medical", tags=["Medical Rule Engine"])


@router.post("/profile", response_model=SuccessResponse[MedicalProfileSummary])
async def get_medical_profile(
    current_user: CurrentUserDep,
    context_builder: Annotated[MedicalContextBuilder, Depends(get_medical_context_builder)],
) -> SuccessResponse[MedicalProfileSummary]:
    """
    Returns the medical-rule-relevant profile derived from the user's
    existing health profile, allergies, and conditions (no separate data
    entry - see MedicalContextBuilder). POST because this recomputes the
    derived view rather than returning a static resource.
    """
    use_case = GetMedicalProfileUseCase(context_builder)
    result = await use_case.execute(current_user.user_id)
    return SuccessResponse(data=result)


@router.post("/evaluate", response_model=SuccessResponse[EvaluateResponse])
async def evaluate_product(
    payload: EvaluateRequest,
    current_user: CurrentUserDep,
    context_builder: Annotated[MedicalContextBuilder, Depends(get_medical_context_builder)],
    engine: Annotated[RuleEngine, Depends(get_rule_engine)],
    evaluation_repo: Annotated[MedicalEvaluationRepository, Depends(get_medical_evaluation_repository)],
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
    nutrition_repo: Annotated[NutritionRepository, Depends(get_nutrition_repository)],
    allergen_repo: Annotated[AllergenRepository, Depends(get_allergen_repository)],
) -> SuccessResponse[EvaluateResponse]:
    use_case = EvaluateProductUseCase(
        context_builder, engine, evaluation_repo, ingredient_repo, nutrition_repo, allergen_repo
    )
    result = await use_case.execute(current_user.user_id, payload)
    return SuccessResponse(data=result)


@router.get("/history", response_model=PaginatedResponse[EvaluationHistoryItem])
async def get_evaluation_history(
    current_user: CurrentUserDep,
    evaluation_repo: Annotated[MedicalEvaluationRepository, Depends(get_medical_evaluation_repository)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[EvaluationHistoryItem]:
    use_case = GetEvaluationHistoryUseCase(evaluation_repo)
    items, meta = await use_case.execute(current_user.user_id, page, limit)
    return PaginatedResponse(data=items, meta=meta)
