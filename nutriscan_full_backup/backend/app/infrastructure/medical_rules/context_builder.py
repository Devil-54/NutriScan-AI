from __future__ import annotations

import uuid
import re

from sqlalchemy import select

from app.domain.enums import ActivityLevel, FitnessGoal, RuleConditionKey
from app.infrastructure.db.models.allergen import Allergen, UserAllergy
from app.infrastructure.db.models.medical_condition import MedicalCondition, UserMedicalCondition
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.infrastructure.medical_rules.rule_context import NutritionSnapshot, RuleContext

_CHILD_AGE_THRESHOLD = 12

# Substring match against the free-text medical_conditions catalog -> fixed rule engine key.
# Order matters: more specific terms ("prediabetes") must be checked before broader ones ("diabetes").
_CONDITION_NAME_MAP: list[tuple[str, RuleConditionKey]] = [
    ("prediabetes", RuleConditionKey.PREDIABETES),
    ("diabetes", RuleConditionKey.DIABETES),
    ("hypertension", RuleConditionKey.HYPERTENSION),
    ("kidney", RuleConditionKey.KIDNEY_DISEASE),
    ("liver", RuleConditionKey.LIVER_DISEASE),
    ("heart", RuleConditionKey.HEART_DISEASE),
    ("coronary", RuleConditionKey.HEART_DISEASE),
    ("cholesterol", RuleConditionKey.HIGH_CHOLESTEROL),
    ("obesity", RuleConditionKey.OBESITY),
    ("pcos", RuleConditionKey.PCOS),
    ("thyroid", RuleConditionKey.THYROID),
]


def _map_condition_name(name: str) -> RuleConditionKey | None:
    lowered = name.lower()
    for term, key in _CONDITION_NAME_MAP:
        if term in lowered:
            return key
    return None


def _split_profile_values(value: str | None) -> set[str]:
    """Normalize the comma/newline separated values collected in profile setup.

    The profile form stores free text while the optional medical catalogue uses
    join tables.  Both are real user data and must participate in evaluation.
    """
    if not value:
        return set()
    return {item.strip() for item in re.split(r"[,;\n|]+", value) if item.strip()}


class MedicalContextBuilder:
    """
    Builds a RuleContext purely from data the user already entered via the
    existing profile/allergy/condition endpoints (Phase 1/2) - no duplicate
    "medical profile" data entry required for Phase 3F.
    """

    def __init__(self, health_profile_repo: HealthProfileRepository) -> None:
        self.health_profile_repo = health_profile_repo
        self.session = health_profile_repo.session

    async def get_condition_keys(self, user_id: uuid.UUID) -> set[RuleConditionKey]:
        result = await self.session.execute(
            select(MedicalCondition.name)
            .join(UserMedicalCondition, UserMedicalCondition.condition_id == MedicalCondition.condition_id)
            .where(UserMedicalCondition.user_id == user_id)
        )
        keys: set[RuleConditionKey] = set()
        for (name,) in result.all():
            mapped = _map_condition_name(name)
            if mapped:
                keys.add(mapped)
        return keys

    async def get_allergy_names(self, user_id: uuid.UUID) -> set[str]:
        result = await self.session.execute(
            select(Allergen.name)
            .join(UserAllergy, UserAllergy.allergen_id == Allergen.allergen_id)
            .where(UserAllergy.user_id == user_id)
        )
        return {name for (name,) in result.all()}

    async def build_profile_summary(self, user_id: uuid.UUID) -> dict:
        profile = await self.health_profile_repo.get_by_user_id(user_id)
        condition_keys = await self.get_condition_keys(user_id)
        allergy_names = await self.get_allergy_names(user_id)

        if profile:
            allergy_names.update(_split_profile_values(profile.allergies))
            for disease in _split_profile_values(profile.diseases):
                mapped = _map_condition_name(disease)
                if mapped:
                    condition_keys.add(mapped)
            if profile.fitness_goal == FitnessGoal.WEIGHT_LOSS:
                condition_keys.add(RuleConditionKey.WEIGHT_LOSS)
            if profile.fitness_goal == FitnessGoal.MUSCLE_GAIN:
                condition_keys.add(RuleConditionKey.WEIGHT_GAIN)
            if profile.activity_level in (ActivityLevel.ACTIVE, ActivityLevel.VERY_ACTIVE):
                condition_keys.add(RuleConditionKey.SPORTS_NUTRITION)
            if profile.pregnancy_status:
                condition_keys.add(RuleConditionKey.PREGNANCY)

        return {
            "conditions": sorted(k.value for k in condition_keys),
            "allergies": sorted(allergy_names),
            "age": profile.age if profile else None,
            "is_pregnant": bool(profile.pregnancy_status) if profile else False,
        }

    async def build_context(
        self, user_id: uuid.UUID, ingredients: list[str], nutrition: NutritionSnapshot, allergen_names: list[str] | None = None
    ) -> RuleContext:
        condition_keys = await self.get_condition_keys(user_id)
        allergy_names = await self.get_allergy_names(user_id)
        profile = await self.health_profile_repo.get_by_user_id(user_id)

        is_pregnant = False
        age = None
        if profile:
            # Always load the latest row inside the request.  Nothing is
            # cached, so the next scan immediately reflects profile edits.
            allergy_names.update(_split_profile_values(profile.allergies))
            for disease in _split_profile_values(profile.diseases):
                mapped = _map_condition_name(disease)
                if mapped:
                    condition_keys.add(mapped)
            age = profile.age
            is_pregnant = bool(profile.pregnancy_status)
            if profile.fitness_goal == FitnessGoal.WEIGHT_LOSS:
                condition_keys.add(RuleConditionKey.WEIGHT_LOSS)
            if profile.fitness_goal == FitnessGoal.MUSCLE_GAIN:
                condition_keys.add(RuleConditionKey.WEIGHT_GAIN)
            if profile.activity_level in (ActivityLevel.ACTIVE, ActivityLevel.VERY_ACTIVE):
                condition_keys.add(RuleConditionKey.SPORTS_NUTRITION)

        return RuleContext(
            ingredients=ingredients,
            allergen_names=allergen_names or [],
            nutrition=nutrition,
            user_conditions=condition_keys,
            user_allergy_names=allergy_names,
            age=age,
            is_pregnant=is_pregnant,
        )
