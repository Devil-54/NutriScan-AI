from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import (
    ActivityLevel,
    AllergySeverity,
    ConditionSeverity,
    DietPreference,
    FitnessGoal,
    Gender,
)


class HealthProfileUpdate(BaseModel):
    age: int = Field(ge=1, le=120)
    gender: Gender
    height_cm: Decimal = Field(gt=0, le=300)
    weight_kg: Decimal = Field(gt=0, le=500)
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    diet_preference: DietPreference
    pregnancy_status: bool | None = None
    period_status: bool | None = None
    allergies: str | None = Field(default=None, max_length=2000)
    diseases: str | None = Field(default=None, max_length=2000)
    emergency_notes: str | None = Field(default=None, max_length=2000)

    @field_validator("height_cm")
    @classmethod
    def sane_height(cls, value: Decimal) -> Decimal:
        # Catches the classic OCR/data-entry error of meters-as-cm (e.g. "1.75" instead of "175").
        if value < 30:
            raise ValueError("height_cm looks implausible - did you mean to enter centimeters?")
        return value


class HealthProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: uuid.UUID
    age: int
    gender: Gender
    height_cm: Decimal
    weight_kg: Decimal
    bmi: Decimal
    activity_level: ActivityLevel
    fitness_goal: FitnessGoal
    diet_preference: DietPreference
    pregnancy_status: bool | None
    period_status: bool | None
    allergies: str | None
    diseases: str | None
    emergency_notes: str | None
    updated_at: datetime


class AllergyItem(BaseModel):
    allergen_id: uuid.UUID
    severity: AllergySeverity


class ConditionItem(BaseModel):
    condition_id: uuid.UUID
    severity: ConditionSeverity | None = None
    notes: str | None = Field(default=None, max_length=1000)
    diagnosed_at: date | None = None


class AllergiesUpdateRequest(BaseModel):
    allergies: list[AllergyItem]


class ConditionsUpdateRequest(BaseModel):
    conditions: list[ConditionItem]


class AllergenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    allergen_id: uuid.UUID
    name: str
    category: str | None


class MedicalConditionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    condition_id: uuid.UUID
    name: str
    category: str | None


class FullProfileRead(BaseModel):
    health_profile: HealthProfileRead | None
    allergies: list[AllergyItem]
    conditions: list[ConditionItem]
