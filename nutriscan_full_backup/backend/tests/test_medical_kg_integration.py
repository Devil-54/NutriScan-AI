from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import ActivityLevel, DietPreference, FitnessGoal, Gender, VerdictStatus
from app.domain.schemas.medical import EvaluateRequest
from app.infrastructure.db.models.allergen import Allergen
from app.infrastructure.db.models.ingredient import Ingredient
from app.infrastructure.db.models.ingredient_allergen import IngredientAllergen
from app.infrastructure.db.models.ingredient_nutrition import IngredientNutrition
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.health_profile import HealthProfile
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.nutrition_repository import NutritionRepository
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder
from app.infrastructure.medical_rules.engine import RuleEngine
from app.use_cases.medical.evaluate_product import EvaluateProductUseCase

pytestmark = pytest.mark.asyncio


async def test_evaluate_pulls_nutrition_and_allergen_from_kg(db_session: AsyncSession) -> None:
    """Simulates post-dataset-import state: an Ingredient row with linked
    IngredientNutrition + IngredientAllergen exists. The caller sends no
    nutrition/allergen_names at all - the use case must still resolve and
    trigger correctly purely from the Knowledge Graph."""
    user = User(name="Test", email="kgtest@example.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()

    ingredient = Ingredient(canonical_name="Peanut Butter")
    db_session.add(ingredient)
    await db_session.flush()

    db_session.add(IngredientNutrition(ingredient_id=ingredient.ingredient_id, sodium_mg=900))
    allergen = Allergen(name="Peanut protein", category="legume")
    db_session.add(allergen)
    await db_session.flush()
    db_session.add(IngredientAllergen(ingredient_id=ingredient.ingredient_id, allergen_id=allergen.allergen_id))

    from app.infrastructure.db.models.allergen import UserAllergy

    db_session.add(UserAllergy(user_id=user.user_id, allergen_id=allergen.allergen_id, severity="severe"))
    await db_session.commit()

    use_case = EvaluateProductUseCase(
        context_builder=MedicalContextBuilder(HealthProfileRepository(db_session)),
        engine=RuleEngine(),
        evaluation_repo=MedicalEvaluationRepository(db_session),
        ingredient_repo=IngredientRepository(db_session),
        nutrition_repo=NutritionRepository(db_session),
        allergen_repo=AllergenRepository(db_session),
    )

    result = await use_case.execute(user.user_id, EvaluateRequest(ingredients=["Peanut Butter"]))

    assert result.status == VerdictStatus.UNSAFE
    assert any("Peanut" in r for r in result.reasons)


async def test_evaluate_uses_latest_free_text_registration_profile(db_session: AsyncSession) -> None:
    """Registration stores allergies/conditions in HealthProfile text fields.
    They must be evaluated even when the optional catalogue tables are empty.
    """
    user = User(name="Profile", email="profile-context@example.com", password_hash="x")
    db_session.add(user)
    await db_session.flush()
    profile = HealthProfile(
        user_id=user.user_id, age=30, gender=Gender.FEMALE,
        height_cm=Decimal("165"), weight_kg=Decimal("60"), bmi=Decimal("22.0"),
        activity_level=ActivityLevel.MODERATE, fitness_goal=FitnessGoal.WEIGHT_LOSS,
        diet_preference=DietPreference.VEGETARIAN, pregnancy_status=True,
        allergies="peanut", diseases="diabetes",
    )
    db_session.add(profile)
    await db_session.commit()

    use_case = EvaluateProductUseCase(
        MedicalContextBuilder(HealthProfileRepository(db_session)), RuleEngine(),
        MedicalEvaluationRepository(db_session), IngredientRepository(db_session),
        NutritionRepository(db_session), AllergenRepository(db_session),
    )
    result = await use_case.execute(user.user_id, EvaluateRequest(ingredients=["Peanut", "Caffeine", "Sugar"]))

    assert result.status == VerdictStatus.UNSAFE
    assert {"food_allergy", "pregnancy", "diabetes"}.issubset(result.triggered_rules)
    # Pregnancy guidance intentionally takes precedence over a stored weight
    # loss goal. Verify the goal rule still runs once pregnancy no longer applies.
    assert "weight_loss" not in result.triggered_rules
    assert any("pregnant" in reason.lower() for reason in result.reasons)

    profile.pregnancy_status = False
    await db_session.commit()
    non_pregnant_result = await use_case.execute(
        user.user_id, EvaluateRequest(ingredients=["Peanut", "Caffeine", "Sugar"])
    )
    assert "weight_loss" in non_pregnant_result.triggered_rules
