"""
Centralized application configuration.

All environment-driven settings are declared here and nowhere else, so the
rest of the codebase depends on `settings` rather than reading `os.environ`
directly. This keeps configuration testable and swappable (e.g. for pytest
fixtures that override `DATABASE_URL`).
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ---- App ----
    PROJECT_NAME: str = "NutriScan"
    ENV: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    # Avoid the host-level DEBUG variable (often set to values such as
    # "release") overriding this application's boolean setting.
    DEBUG: bool = Field(default=False, validation_alias="NUTRISCAN_DEBUG")

    # ---- Database ----
    DATABASE_URL: str = "postgresql+asyncpg://localhost:5432/nutriscan"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://localhost:5432/nutriscan"

    # ---- JWT ----
    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY_PATH: str = "keys/private_key.pem"
    JWT_PUBLIC_KEY_PATH: str = "keys/public_key.pem"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- Security ----
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # ---- Rate limiting ----
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_UPLOAD: str = "20/hour"

    # ---- File upload / storage (Phase 3B - Food Scan Infrastructure) ----
    STORAGE_ROOT_DIR: str = "storage/uploads"
    STORAGE_BACKEND: str = "local"  # "local" now; "s3"/"cloudinary" adapters can be swapped in later
    MAX_UPLOAD_SIZE_MB: int = 8
    ALLOWED_IMAGE_EXTENSIONS: str = "jpg,jpeg,png,webp"
    ALLOWED_IMAGE_MIME_TYPES: str = "image/jpeg,image/png,image/webp"
    MIN_IMAGE_WIDTH_PX: int = 300
    MIN_IMAGE_HEIGHT_PX: int = 300
    THUMBNAIL_MAX_DIMENSION_PX: int = 320
    MAX_UPLOADS_PER_USER_PER_DAY: int = 50
    SCAN_EXPIRATION_DAYS: int = 90
    DELETED_SCAN_RETENTION_DAYS: int = 30

    # ---- Knowledge graph datasets ----
    # Paths stay relative to the backend directory so the checked-in dataset
    # layout can be used unchanged on every developer machine.
    DATASET_ROOT: str = "dataset"
    OPENFOODFACTS_DATASET_PATH: str = "dataset/en.openfoodfacts.org.products.csv.gz"
    USDA_BRANDED_DATASET_PATH: str = (
        "dataset/FoodData_Central_branded_food_csv_2026-04-30/"
        "FoodData_Central_branded_food_csv_2026-04-30/branded_food.csv"
    )
    USDA_SUPPORTING_DATASET_DIR: str = "dataset/FoodData_Central_Supporting_Data_csv_2022-10-28"
    ALLERGENS_DATASET_PATH: str = "dataset/allergens.json"
    INGREDIENT_ALIASES_DATASET_PATH: str = "dataset/ingredient_aliases.json"
    INS_ADDITIVES_DATASET_PATH: str = "dataset/ins_additives.json"

    # ---- OCR ----
    OCR_MIN_CONFIDENCE: float = 40.0
    OCR_TIMEOUT_SECONDS: int = 30
    OCR_BLUR_THRESHOLD: float = 100.0
    OCR_LANGUAGES: str = "en"
    OCR_TARGET_MAX_DIMENSION: int = 1600
    OCR_MODEL_DIR: str = "storage/paddleocr"

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_image_extensions_set(self) -> set[str]:
        return {ext.strip().lower().lstrip(".") for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",") if ext.strip()}

    @property
    def allowed_image_mime_types_set(self) -> set[str]:
        return {mime.strip().lower() for mime in self.ALLOWED_IMAGE_MIME_TYPES.split(",") if mime.strip()}

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def jwt_private_key(self) -> str:
        return Path(self.JWT_PRIVATE_KEY_PATH).read_text()

    @property
    def jwt_public_key(self) -> str:
        return Path(self.JWT_PUBLIC_KEY_PATH).read_text()


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
