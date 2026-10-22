from __future__ import annotations

import uuid

from app.domain.schemas.medical import EvaluateRequest, EvaluateResponse
from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.nutrition_repository import NutritionRepository
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder
from app.infrastructure.medical_rules.engine import RuleEngine
from app.infrastructure.medical_rules.evaluation_service import ProductEvaluationService
from app.infrastructure.medical_rules.rule_context import NutritionSnapshot


class EvaluateProductUseCase:
    def __init__(
        self,
        context_builder: MedicalContextBuilder,
        engine: RuleEngine,
        evaluation_repo: MedicalEvaluationRepository,
        ingredient_repo: IngredientRepository | None = None,
        nutrition_repo: NutritionRepository | None = None,
        allergen_repo: AllergenRepository | None = None,
    ) -> None:
        self.evaluation_repo = evaluation_repo
        self.evaluation_service = ProductEvaluationService(
            context_builder, engine, ingredient_repo, nutrition_repo, allergen_repo
        )

    async def execute(self, user_id: uuid.UUID, payload: EvaluateRequest) -> EvaluateResponse:
        caller_nutrition = NutritionSnapshot(**payload.nutrition.model_dump()) if payload.nutrition else None

        verdict, _context, _kg_ratio = await self.evaluation_service.evaluate(
            user_id=user_id,
            ingredients=payload.ingredients,
            nutrition=caller_nutrition,
            allergen_names=payload.allergen_names,
        )

        evaluation = MedicalEvaluation(
            user_id=user_id,
            ingredients=payload.ingredients,
            status=verdict.status.value,
            risk_level=verdict.risk_level.value,
            severity=verdict.severity.value,
            health_score=verdict.health_score,
            reasons=verdict.reasons,
            recommendations=verdict.recommendations,
            safe_ingredients=verdict.safe_ingredients,
            unsafe_ingredients=verdict.unsafe_ingredients,
            triggered_rules=verdict.triggered_rules,
        )
        self.evaluation_repo.add(evaluation)
        await self.evaluation_repo.commit()

        return EvaluateResponse(
            status=verdict.status,
            risk_level=verdict.risk_level,
            severity=verdict.severity,
            health_score=verdict.health_score,
            reasons=verdict.reasons,
            recommendations=verdict.recommendations,
            safe_ingredients=verdict.safe_ingredients,
            unsafe_ingredients=verdict.unsafe_ingredients,
            triggered_rules=verdict.triggered_rules,
        )
