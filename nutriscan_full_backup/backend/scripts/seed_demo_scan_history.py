"""Update the Lay's college-demo label through the normal evaluator.

This development-only utility never creates a user or a UI-only record. It
updates only the matching Lay's scan row owned by the supplied user, or
creates a normal scan/OCR row when one is missing, then persists its
rule-engine result in ``medical_evaluations``. Maggi and Quaker are
deliberately not read, modified, or re-evaluated. Re-running it is
idempotent: the matching scan retains its scan ID and gets one fresh saved
evaluation.

Usage: poetry run python -m scripts.seed_demo_scan_history --user-id <UUID>
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import uuid

from sqlalchemy import select

from app.domain.schemas.medical import NutritionInput
from app.domain.schemas.recommendation import RecommendationRequest
from app.domain.enums import OcrEngine, OcrStatus, ProcessingStage, ScanStatus
from app.infrastructure.db.models.medical_evaluation import MedicalEvaluation
from app.infrastructure.db.models.ocr_result import OcrResult
from app.infrastructure.db.models.scan_session import ScanSession
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.health_profile_repository import HealthProfileRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.repositories.medical_evaluation_repository import MedicalEvaluationRepository
from app.infrastructure.db.repositories.nutrition_repository import NutritionRepository
from app.infrastructure.db.repositories.scan_repository import ScanRepository
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.medical_rules.context_builder import MedicalContextBuilder
from app.infrastructure.medical_rules.engine import RuleEngine
from app.infrastructure.medical_rules.evaluation_service import ProductEvaluationService
from app.infrastructure.recommendation.engine import RecommendationEngine
from app.use_cases.recommendation.generate_recommendation import GenerateRecommendationUseCase


# These normalized lists and nutrition values are transcribed from the three
# supplied labels.  This is intentionally product-specific: it is the saved
# OCR transcript associated with each individual scan, not a shared demo list.
DEMO_PRODUCTS = {
    "Maggi.png": {
        "name": "Maggi 2-Minute Masala Noodles",
        "ingredients": [
            "refined wheat flour", "palm oil", "iodized salt", "wheat gluten",
            "seasoning / taste maker", "onion", "garlic", "ginger", "coriander",
            "turmeric", "cumin", "fenugreek", "black pepper", "nutmeg",
            "cardamom", "flavour enhancer INS 621",
        ],
        "raw_ocr": """Ingredients: Refined wheat flour, palm oil, iodized salt, wheat gluten, seasoning / taste maker, onion, garlic, ginger, coriander, turmeric, cumin, fenugreek, black pepper, nutmeg, cardamom, flavour enhancer INS 621.""",
        "nutrition": None,
        "display_nutrition": None,
    },
    "Lay's Potato Chips.png": {
        "name": "Lay's Potato Chips",
        "ingredients": ["potatoes", "vegetable oil", "sunflower oil", "corn oil", "canola oil", "salt"],
        "raw_ocr": """Ingredients: Potatoes, vegetable oil (sunflower oil, corn and/or canola oil), salt. Nutrition Facts: Calories 160; Total Fat 10 g; Saturated Fat 1.5 g; Trans Fat 0 g; Cholesterol 0 mg; Sodium 170 mg; Potassium 350 mg; Total Carbohydrate 15 g; Dietary Fiber 1 g; Sugars less than 1 g; Protein 2 g.""",
        "nutrition": NutritionInput(
            calories=160, fat_g=10, saturated_fat_g=1.5, trans_fat_g=0,
            cholesterol_mg=0, sodium_mg=170, potassium_mg=350,
            carbohydrates_g=15, fiber_g=1, protein_g=2,
        ),
        "display_nutrition": {
            "calories": 160, "fat_g": 10, "saturated_fat_g": 1.5,
            "trans_fat_g": 0, "cholesterol_mg": 0, "sodium_mg": 170,
            "potassium_mg": 350, "carbohydrates_g": 15, "fiber_g": 1,
            "sugar_g": "Less than 1", "protein_g": 2,
        },
    },
    "Quaker Original Instant Oatmeal.png": {
        "name": "Quaker Original Instant Oatmeal",
        "ingredients": ["whole grain oats", "calcium carbonate", "salt", "reduced iron"],
        "raw_ocr": """Ingredients: Whole grain oats, calcium carbonate, salt, reduced iron. Nutrition Facts: Calories 100; Total Fat 2 g; Saturated Fat 0.5 g; Trans Fat 0 g; Cholesterol 0 mg; Sodium 75 mg; Total Carbohydrate 19 g; Dietary Fiber 3 g; Total Sugars 0 g; Protein 4 g; Calcium 120 mg; Iron 8 mg; Potassium 100 mg.""",
        "nutrition": NutritionInput(
            calories=100, fat_g=2, saturated_fat_g=0.5, trans_fat_g=0,
            cholesterol_mg=0, sodium_mg=75, potassium_mg=100,
            calcium_mg=120, iron_mg=8, carbohydrates_g=19, fiber_g=3,
            sugar_g=0, protein_g=4,
        ),
        "display_nutrition": {
            "calories": 100, "fat_g": 2, "saturated_fat_g": 0.5,
            "trans_fat_g": 0, "cholesterol_mg": 0, "sodium_mg": 75,
            "potassium_mg": 100, "carbohydrates_g": 19, "fiber_g": 3,
            "sugar_g": 0, "protein_g": 4, "calcium_mg": 120, "iron_mg": 8,
        },
    },
}

# This focused importer intentionally leaves the correct Maggi and Quaker
# evaluations as saved. Do not broaden this list without an explicit update.
TARGET_FILENAMES = ("Lay's Potato Chips.png",)


def _demo_scan(filename: str, user_id: uuid.UUID) -> ScanSession:
    """Create a normal scan row when the label was not uploaded beforehand.

    The source image itself is not bundled with this utility, so the storage
    reference is explicitly a development import marker.  All information
    displayed by History comes from the real scan/OCR/evaluation tables.
    """
    checksum = hashlib.sha256(f"nutriscan-demo-label:{filename}".encode()).hexdigest()
    return ScanSession(
        user_id=user_id, original_filename=filename,
        storage_path=f"demo-imports/{checksum}.png", thumbnail_path=None,
        mime_type="image/png", file_size_bytes=0, checksum_sha256=checksum,
        width_px=1, height_px=1, status=ScanStatus.COMPLETED,
        processing_stage=ProcessingStage.DONE,
    )


async def seed_demo_history(user_id: uuid.UUID) -> list[tuple[str, int, str]]:
    async with AsyncSessionLocal() as session:
        scan_repo = ScanRepository(session)
        evaluation_repo = MedicalEvaluationRepository(session)
        profile_repo = HealthProfileRepository(session)
        evaluator = ProductEvaluationService(
            MedicalContextBuilder(profile_repo), RuleEngine(), IngredientRepository(session),
            NutritionRepository(session), AllergenRepository(session),
        )
        use_case = GenerateRecommendationUseCase(
            evaluator, RecommendationEngine(product_repo=FoodProductRepository(session)),
            profile_repo, evaluation_repo, scan_repo,
        )
        scans = list((await session.execute(
            select(scan_repo.model).where(
                scan_repo.model.user_id == user_id,
                scan_repo.model.original_filename.in_(TARGET_FILENAMES),
                scan_repo.model.deleted_at.is_(None),
            )
        )).scalars())
        by_filename = {scan.original_filename: scan for scan in scans}
        saved: list[tuple[str, int, str]] = []
        for filename in TARGET_FILENAMES:
            product = DEMO_PRODUCTS[filename]
            scan = by_filename.get(filename)
            if scan is None:
                scan = _demo_scan(filename, user_id)
                session.add(scan)
                await session.flush()
            scan.status = ScanStatus.COMPLETED
            scan.processing_stage = ProcessingStage.DONE
            previous = await session.scalar(
                select(MedicalEvaluation).where(MedicalEvaluation.scan_id == scan.scan_id)
            )
            if previous is not None:
                await session.delete(previous)
                await session.flush()

            ocr = await session.scalar(select(OcrResult).where(OcrResult.scan_id == scan.scan_id))
            if ocr is None:
                ocr = OcrResult(scan_id=scan.scan_id, status=OcrStatus.COMPLETED, engine=OcrEngine.PADDLEOCR)
                session.add(ocr)
            ocr.ingredients_text = product["raw_ocr"]
            ocr.status = OcrStatus.COMPLETED

            # Existing scans keep their original scan timestamp.  A newly
            # created development-import row receives its normal DB timestamp.
            result = await use_case.execute(
                user_id,
                RecommendationRequest(
                    scan_id=scan.scan_id,
                    product_name=product["name"],
                    ingredients=product["ingredients"],
                    nutrition=product["nutrition"],
                ),
            )
            # Preserve presentation-only label wording such as "Less than 1"
            # alongside the numeric values supplied to the rule engine.
            if product["display_nutrition"] is not None:
                evaluation = await session.scalar(
                    select(MedicalEvaluation).where(MedicalEvaluation.scan_id == scan.scan_id)
                )
                assert evaluation is not None
                evaluation.nutrition_snapshot = product["display_nutrition"]
                await session.commit()
            saved.append((product["name"], result.recommendation_score, result.risk_level.value))
        return saved


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist evaluation results for the uploaded college-demo labels.")
    parser.add_argument("--user-id", required=True, type=uuid.UUID)
    args = parser.parse_args()
    for name, score, risk in asyncio.run(seed_demo_history(args.user_id)):
        print(f"{name}: score={score}, risk={risk}")


if __name__ == "__main__":
    main()
