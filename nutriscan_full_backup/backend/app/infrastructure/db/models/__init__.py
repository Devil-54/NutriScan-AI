"""
Import every model here so `Base.metadata` is fully populated for Alembic
autogenerate, and so other modules can do `from app.infrastructure.db.models import User`.
"""
from app.infrastructure.db.models.additive import Additive
from app.infrastructure.db.models.allergen import Allergen, UserAllergy
from app.infrastructure.db.models.audit_log import AuditLog
from app.infrastructure.db.models.category import Category
from app.infrastructure.db.models.food_product import FoodProduct, ProductIngredient
from app.infrastructure.db.models.health_profile import HealthProfile
from app.infrastructure.db.models.import_job import ImportJob
from app.infrastructure.db.models.ingredient import Ingredient, IngredientAlias
from app.infrastructure.db.models.ingredient_allergen import IngredientAllergen
from app.infrastructure.db.models.ingredient_nutrition import IngredientNutrition
from app.infrastructure.db.models.ingredient_parse import IngredientParse
from app.infrastructure.db.models.medical_condition import MedicalCondition, UserMedicalCondition
from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.models.ocr_result import OcrResult
from app.infrastructure.db.models.refresh_token import RefreshToken
from app.infrastructure.db.models.scan_session import ScanSession
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.user_settings import UserSettings

__all__ = [
    "Additive",
    "Allergen",
    "UserAllergy",
    "AuditLog",
    "Category",
    "FoodProduct",
    "ProductIngredient",
    "HealthProfile",
    "ImportJob",
    "Ingredient",
    "IngredientAlias",
    "IngredientAllergen",
    "IngredientNutrition",
    "IngredientParse",
    "MedicalCondition",
    "MedicalEvaluation",
    "UserMedicalCondition",
    "OcrResult",
    "RefreshToken",
    "ScanSession",
    "User",
    "UserSettings",
]
