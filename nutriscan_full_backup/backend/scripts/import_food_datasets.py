"""Import the configured OpenFoodFacts and USDA branded CSV exports.

The OpenFoodFacts export is read directly from its ``.csv.gz`` file; it is
never extracted to disk. Run after migrations and ``scripts.seed``:

    poetry run python -m scripts.import_food_datasets
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.infrastructure.dataset.csv_loader import DatasetLoader
from app.infrastructure.dataset.importers.open_food_facts_importer import OpenFoodFactsImporter
from app.infrastructure.dataset.importers.usda_importer import UsdaImporter
from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.import_job_repository import ImportJobRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.db.models.import_job import ImportJob


async def _import(importer_type: type[OpenFoodFactsImporter] | type[UsdaImporter], path: str) -> None:
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    async with AsyncSessionLocal() as session:
        importer = importer_type(
            DatasetLoader(dataset_path),
            IngredientRepository(session),
            FoodProductRepository(session),
            CategoryRepository(session),
            ImportJobRepository(session),
        )
        existing_job = await session.scalar(
            select(ImportJob)
            .where(ImportJob.source == importer.source_name, ImportJob.status == "running")
            .order_by(ImportJob.updated_at.desc())
            .limit(1)
        )
        job = await importer.run(batch_size=1_000, job=existing_job)
        print(
            f"{job.source}: status={job.status}, processed={job.processed_rows}, "
            f"new_ingredients={job.inserted_count}, duplicates={job.skipped_duplicate_count}, errors={job.error_count}"
        )
        if job.status != "completed":
            raise RuntimeError(job.last_error or f"{job.source} import failed")


async def main() -> None:
    await _import(OpenFoodFactsImporter, settings.OPENFOODFACTS_DATASET_PATH)
    await _import(UsdaImporter, settings.USDA_BRANDED_DATASET_PATH)


if __name__ == "__main__":
    asyncio.run(main())
