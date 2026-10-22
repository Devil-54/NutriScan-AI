from __future__ import annotations

import uuid

from app.domain.schemas.recommendation import (
    AlternativeItem,
    IngredientWarningItem,
    RecommendationRequest,
    RecommendationResponse,
)
from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.medical_rules.evaluation_service import ProductEvaluationService
from app.infrastructure.medical_rules.rule_context import NutritionSnapshot
from app.infrastructure.recommendation.engine import PersonalizationProfile, RecommendationEngine
from app.infrastructure.recommendation.models import RecommendationResult
from app.core.logging import get_logger

logger = get_logger()


class GenerateRecommendationUseCase:
    """
    Reuses ProductEvaluationService (same KG resolution + Medical Rule
    Engine pass used by /medical/evaluate) so the rule engine runs exactly
    once per request, then layers RecommendationEngine's personalization
    on top. Persists into the same `medical_evaluations` table Phase 3F
    already created (extended with recommendation columns), not a new table.
    """

    def __init__(
        self,
        evaluation_service: ProductEvaluationService,
        recommendation_engine: RecommendationEngine,
        health_profile_repo: HealthProfileRepository,
        evaluation_repo: MedicalEvaluationRepository,
        scan_repo: ScanRepository | None = None,
    ) -> None:
        self.evaluation_service = evaluation_service
        self.recommendation_engine = recommendation_engine
        self.health_profile_repo = health_profile_repo
        self.evaluation_repo = evaluation_repo
        self.scan_repo = scan_repo

    async def execute(self, user_id: uuid.UUID, payload: RecommendationRequest) -> RecommendationResponse:
        scan = None
        if payload.scan_id is not None:
            if self.scan_repo is None:
                raise RuntimeError("Scan repository is required for a scanner evaluation")
            # This ownership check prevents a caller from attaching a result to
            # another user's scan, and makes scan -> evaluation a one-to-one link.
            scan = await self.scan_repo.get_owned_by_id(payload.scan_id, user_id)
            if scan is None:
                from app.core.exceptions import NotFoundException
                raise NotFoundException("Scan not found")
        nutrition = NutritionSnapshot(**payload.nutrition.model_dump()) if payload.nutrition else None

        verdict, context, kg_match_ratio = await self.evaluation_service.evaluate(
            user_id=user_id,
            ingredients=payload.ingredients,
            nutrition=nutrition,
            allergen_names=payload.allergen_names,
        )

        health_profile = await self.health_profile_repo.get_by_user_id(user_id)
        profile = PersonalizationProfile.from_health_profile(health_profile)
        profile_snapshot = {
            "conditions": sorted(condition.value for condition in context.user_conditions),
            "allergies": sorted(context.user_allergy_names),
            "pregnant": context.is_pregnant,
            # Preserve the effective goal used by this historical evaluation.
            # Pregnancy must never retain a weight-loss recommendation.
            "fitness_goal": profile.displayed_fitness_goal,
            "activity_level": health_profile.activity_level.value if health_profile and health_profile.activity_level else None,
            "diet_preference": profile.diet_preference,
            "bmi": profile.bmi,
            "age": profile.age,
            "gender": profile.gender,
            "height_cm": profile.height_cm,
            "weight_kg": profile.weight_kg,
        }

        logger.bind(event="RECOMMENDATION_START", user_id=str(user_id)).info("Recommendation generation started")
        try:
            result = await self.recommendation_engine.generate(verdict, context, profile, kg_match_ratio)
        except Exception as exc:
            # Recommendations are an enhancement.  Preserve the real medical
            # verdict when a recommendation source or explainer is unavailable.
            logger.bind(
                event="RECOMMENDATION_FAILED",
                user_id=str(user_id),
                exception_type=type(exc).__name__,
            ).error("Recommendation generation failed; returning medical evaluation")
            result = RecommendationResult(
                safe_foods=verdict.safe_ingredients,
                unsafe_foods=verdict.unsafe_ingredients,
                recommendation_score=verdict.health_score,
                confidence_score=max(40, int(40 + kg_match_ratio * 55)),
                reasons=verdict.reasons,
                health_tips=["No relevant personalized concern was detected." ] if not verdict.reasons else [],
            )
        logger.bind(event="RECOMMENDATION_COMPLETE", user_id=str(user_id)).info("Recommendation generation completed")

        evaluation = MedicalEvaluation(
            user_id=user_id,
            scan_id=payload.scan_id,
            ingredients=payload.ingredients,
            status=verdict.status.value,
            risk_level=verdict.risk_level.value,
            severity=verdict.severity.value,
            health_score=result.recommendation_score,
            reasons=result.reasons,
            recommendations=[a.suggestion for a in result.alternatives] + result.health_tips,
            safe_ingredients=result.safe_foods,
            unsafe_ingredients=result.unsafe_foods,
            triggered_rules=verdict.triggered_rules,
            profile_snapshot=profile_snapshot,
            nutrition_snapshot=payload.nutrition.model_dump(exclude_none=True) if payload.nutrition else None,
            alternatives=[{"suggestion": a.suggestion, "reason": a.reason} for a in result.alternatives],
            health_tips=result.health_tips,
            nutrition_advice=result.nutrition_advice,
            lifestyle_advice=result.lifestyle_advice,
            ingredient_warnings=[{"ingredient": w.ingredient, "reason": w.reason} for w in result.ingredient_warnings],
            confidence_score=result.confidence_score,
        )
        if scan is not None and payload.product_name and payload.product_name.strip():
            scan.product_name = payload.product_name.strip()
        self.evaluation_repo.add(evaluation)
        await self.evaluation_repo.commit()
        logger.bind(event="SCAN_COMPLETE", user_id=str(user_id)).info("Personalized evaluation completed")

        return RecommendationResponse(
            status=verdict.status,
            risk_level=verdict.risk_level,
            safe_foods=result.safe_foods,
            unsafe_foods=result.unsafe_foods,
            alternatives=[AlternativeItem(suggestion=a.suggestion, reason=a.reason) for a in result.alternatives],
            health_tips=result.health_tips,
            nutrition_advice=result.nutrition_advice,
            lifestyle_advice=result.lifestyle_advice,
            ingredient_warnings=[
                IngredientWarningItem(ingredient=w.ingredient, reason=w.reason) for w in result.ingredient_warnings
            ],
            recommendation_score=result.recommendation_score,
            confidence_score=result.confidence_score,
            reasons=result.reasons,
        )
