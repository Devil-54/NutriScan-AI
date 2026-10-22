import uuid
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ForbiddenException, ServiceUnavailableException, UnauthorizedException
from app.core.security import TokenType, decode_token
from app.domain.enums import UserRole
from app.infrastructure.db.repositories.additive_repository import AdditiveRepository
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.audit_log_repository import AuditLogRepository
from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.infrastructure.db.repositories.import_job_repository import ImportJobRepository
from app.infrastructure.db.repositories.ingredient_parse_repository import IngredientParseRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.nutrition_repository import NutritionRepository
from app.infrastructure.db.repositories.ocr_result_repository import OcrResultRepository
from app.infrastructure.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.session import get_db
from app.infrastructure.email.email_service import EmailService, LoggingEmailService
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder
from app.infrastructure.medical_rules.engine import RuleEngine
from app.infrastructure.medical_rules.evaluation_service import ProductEvaluationService
from app.infrastructure.recommendation.engine import RecommendationEngine
from app.infrastructure.ocr.ocr_service import OcrService
from app.infrastructure.storage.scan_storage_service import ScanStorageService
from app.infrastructure.storage.storage_backend import LocalStorageBackend, StorageBackend
from app.infrastructure.storage.virus_scanner import NoOpVirusScanner, VirusScanner

_bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]

# Single process-wide storage backend instance - safe to share since it holds
# no per-request state (just the resolved root directory).
_storage_backend = LocalStorageBackend()


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_device_info(request: Request) -> str | None:
    return request.headers.get("user-agent")


def get_email_service() -> EmailService:
    return LoggingEmailService()


# ---- Repository factories ----


def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)


def get_refresh_token_repository(db: DbSession) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


def get_health_profile_repository(db: DbSession) -> HealthProfileRepository:
    return HealthProfileRepository(db)


def get_audit_log_repository(db: DbSession) -> AuditLogRepository:
    return AuditLogRepository(db)


def get_scan_repository(db: DbSession) -> ScanRepository:
    return ScanRepository(db)


def get_storage_backend() -> StorageBackend:
    return _storage_backend


def get_scan_storage_service(
    backend: Annotated[StorageBackend, Depends(get_storage_backend)],
) -> ScanStorageService:
    return ScanStorageService(backend)


def get_virus_scanner() -> VirusScanner:
    if settings.ENV.strip().lower() not in {"development", "test"}:
        raise ServiceUnavailableException(
            "Uploads are disabled until a non-development virus scanner is configured",
            error_code="VIRUS_SCANNER_UNAVAILABLE",
        )
    return NoOpVirusScanner()


def get_ocr_result_repository(db: DbSession) -> OcrResultRepository:
    return OcrResultRepository(db)


def get_ocr_service() -> OcrService:
    from app.infrastructure.ocr.ocr_engines import get_paddle_engine

    engine = get_paddle_engine()
    return OcrService(primary=engine, fallback=engine)


def get_ingredient_parse_repository(db: DbSession) -> IngredientParseRepository:
    return IngredientParseRepository(db)


def get_ingredient_repository(db: DbSession) -> IngredientRepository:
    return IngredientRepository(db)


def get_food_product_repository(db: DbSession) -> FoodProductRepository:
    return FoodProductRepository(db)


def get_category_repository(db: DbSession) -> CategoryRepository:
    return CategoryRepository(db)


def get_import_job_repository(db: DbSession) -> ImportJobRepository:
    return ImportJobRepository(db)


def get_allergen_repository(db: DbSession) -> AllergenRepository:
    return AllergenRepository(db)


def get_additive_repository(db: DbSession) -> AdditiveRepository:
    return AdditiveRepository(db)


def get_nutrition_repository(db: DbSession) -> NutritionRepository:
    return NutritionRepository(db)


def get_medical_evaluation_repository(db: DbSession) -> MedicalEvaluationRepository:
    return MedicalEvaluationRepository(db)


def get_medical_context_builder(db: DbSession) -> MedicalContextBuilder:
    return MedicalContextBuilder(HealthProfileRepository(db))


def get_rule_engine() -> RuleEngine:
    return RuleEngine()


def get_product_evaluation_service(
    context_builder: Annotated[MedicalContextBuilder, Depends(get_medical_context_builder)],
    engine: Annotated[RuleEngine, Depends(get_rule_engine)],
    ingredient_repo: Annotated[IngredientRepository, Depends(get_ingredient_repository)],
    nutrition_repo: Annotated[NutritionRepository, Depends(get_nutrition_repository)],
    allergen_repo: Annotated[AllergenRepository, Depends(get_allergen_repository)],
) -> ProductEvaluationService:
    return ProductEvaluationService(context_builder, engine, ingredient_repo, nutrition_repo, allergen_repo)


def get_recommendation_engine(
    product_repo: Annotated[FoodProductRepository, Depends(get_food_product_repository)],
) -> RecommendationEngine:
    return RecommendationEngine(product_repo=product_repo)


# ---- Auth context ----


class CurrentUser:
    __slots__ = ("user_id", "role")

    def __init__(self, user_id: uuid.UUID, role: UserRole) -> None:
        self.user_id = user_id
        self.role = role


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedException("Missing authentication token", error_code="MISSING_TOKEN")

    payload = decode_token(credentials.credentials, expected_type=TokenType.ACCESS)
    return CurrentUser(user_id=uuid.UUID(payload["sub"]), role=UserRole(payload["role"]))


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_role(*allowed_roles: UserRole):
    async def _checker(current_user: CurrentUserDep) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise ForbiddenException("You do not have permission to perform this action", error_code="FORBIDDEN_ROLE")
        return current_user

    return _checker
