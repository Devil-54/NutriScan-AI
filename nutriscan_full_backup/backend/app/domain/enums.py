"""
Domain-level enums shared between SQLAlchemy models and Pydantic schemas.

Kept in one place (not duplicated per-layer) so a new value only ever needs
to be added once.
"""
from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class ActivityLevel(StrEnum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"


class FitnessGoal(StrEnum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    GENERAL_HEALTH = "general_health"


class DietPreference(StrEnum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    NON_VEGETARIAN = "non_vegetarian"
    EGGETARIAN = "eggetarian"
    JAIN = "jain"
    OTHER = "other"


class AllergySeverity(StrEnum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    ANAPHYLACTIC = "anaphylactic"


class ConditionSeverity(StrEnum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class UnitSystem(StrEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class ScanStatus(StrEnum):
    """
    Lifecycle of a scan session. Phase 3B only ever produces UPLOADED
    (upload succeeded, nothing further has happened yet). QUEUED/PROCESSING/
    COMPLETED/FAILED are reserved for the OCR/Analysis phases that will
    consume this infrastructure - the column and transitions exist now so
    that phase doesn't need a schema change, only new writers.
    """

    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStage(StrEnum):
    """Fine-grained stage within PROCESSING, for progress reporting in later phases."""

    NOT_STARTED = "not_started"
    OCR = "ocr"
    INGREDIENT_RESOLUTION = "ingredient_resolution"
    RISK_ANALYSIS = "risk_analysis"
    EXPLANATION = "explanation"
    DONE = "done"


class OcrStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OcrEngine(StrEnum):
    PADDLEOCR = "PaddleOCR"


class VerdictStatus(StrEnum):
    SAFE = "safe"
    WARNING = "warning"
    UNSAFE = "unsafe"


class RiskLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RuleConditionKey(StrEnum):
    """Internal condition keys evaluated by the Medical Rule Engine (Phase 3F).
    Distinct from the free-text `medical_conditions` catalog table - these are
    the fixed set the rule engine knows how to reason about."""

    FOOD_ALLERGY = "food_allergy"
    DIABETES = "diabetes"
    PREDIABETES = "prediabetes"
    HYPERTENSION = "hypertension"
    HEART_DISEASE = "heart_disease"
    KIDNEY_DISEASE = "kidney_disease"
    LIVER_DISEASE = "liver_disease"
    PREGNANCY = "pregnancy"
    CHILD = "child"
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    SPORTS_NUTRITION = "sports_nutrition"
    HIGH_CHOLESTEROL = "high_cholesterol"
    OBESITY = "obesity"
    PCOS = "pcos"
    THYROID = "thyroid"
    PRODUCT_QUALITY = "product_quality"
    PROCESSED_SNACK = "processed_snack"
    LOW_NUTRIENT_DENSITY = "low_nutrient_density"
