from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.dataset.csv_loader import DatasetLoader
from app.infrastructure.dataset.importers.open_food_facts_importer import OpenFoodFactsImporter
from app.infrastructure.dataset.importers.usda_importer import UsdaImporter
from app.infrastructure.db.models.ingredient import Ingredient
from app.infrastructure.db.models.import_job import ImportJob
from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.import_job_repository import ImportJobRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository

pytestmark = pytest.mark.asyncio

OFF_CSV = (
    "code,product_name,brands,categories,ingredients_text\n"
    "1001,Choco Bar,BrandA,Snacks,Sugar\n"
    "1002,Salt Chips,BrandB,Snacks,Salt\n"
    "1003,Rice Cake,BrandC,Snacks,Rice\n"
)

USDA_CSV = (
    "fdc_id,description,brand_owner,branded_food_category,ingredients,gtin_upc\n"
    "501,Wheat Bread,BrandZ,Bakery,Wheat Flour,1112223\n"
    "502,Corn Flakes,BrandY,Cereal,Corn,1112224\n"
)


def _make_repos(db_session: AsyncSession):
    return (
        IngredientRepository(db_session),
        FoodProductRepository(db_session),
        CategoryRepository(db_session),
        ImportJobRepository(db_session),
    )


class TestOpenFoodFactsImporter:
    async def test_imports_all_rows(self, db_session: AsyncSession, tmp_path) -> None:
        csv_path = tmp_path / "off.csv"
        csv_path.write_text(OFF_CSV)
        ing_repo, prod_repo, cat_repo, job_repo = _make_repos(db_session)

        importer = OpenFoodFactsImporter(DatasetLoader(csv_path), ing_repo, prod_repo, cat_repo, job_repo)
        job = await importer.run(batch_size=2)

        assert job.status == "completed"
        assert job.processed_rows == 3
        assert job.inserted_count == 3

        result = await db_session.execute(select(Ingredient))
        assert len(result.scalars().all()) == 3

    async def test_missing_file_marks_job_failed_not_raises(self, db_session: AsyncSession, tmp_path) -> None:
        ing_repo, prod_repo, cat_repo, job_repo = _make_repos(db_session)
        importer = OpenFoodFactsImporter(DatasetLoader(tmp_path / "missing.csv"), ing_repo, prod_repo, cat_repo, job_repo)

        job = await importer.run()
        assert job.status == "failed"
        assert job.last_error

    async def test_duplicate_run_skips_existing(self, db_session: AsyncSession, tmp_path) -> None:
        csv_path = tmp_path / "off.csv"
        csv_path.write_text(OFF_CSV)
        ing_repo, prod_repo, cat_repo, job_repo = _make_repos(db_session)

        importer1 = OpenFoodFactsImporter(DatasetLoader(csv_path), ing_repo, prod_repo, cat_repo, job_repo)
        await importer1.run()

        importer2 = OpenFoodFactsImporter(DatasetLoader(csv_path), ing_repo, prod_repo, cat_repo, job_repo)
        job2 = await importer2.run()

        assert job2.skipped_duplicate_count == 3
        assert job2.inserted_count == 0

    async def test_malformed_row_skipped_not_fatal(self, db_session: AsyncSession, tmp_path) -> None:
        csv_path = tmp_path / "off_bad.csv"
        csv_path.write_text(
            "code,product_name,brands,categories,ingredients_text\n"
            ",MissingCode,BrandA,Snacks,Sugar\n"
            "1005,OK Product,BrandA,Snacks,Salt\n"
        )
        ing_repo, prod_repo, cat_repo, job_repo = _make_repos(db_session)

        importer = OpenFoodFactsImporter(DatasetLoader(csv_path), ing_repo, prod_repo, cat_repo, job_repo)
        job = await importer.run()

        assert job.status == "completed"
        assert job.inserted_count == 1


class TestUsdaImporter:
    async def test_imports_rows(self, db_session: AsyncSession, tmp_path) -> None:
        csv_path = tmp_path / "usda.csv"
        csv_path.write_text(USDA_CSV)
        ing_repo, prod_repo, cat_repo, job_repo = _make_repos(db_session)

        importer = UsdaImporter(DatasetLoader(csv_path), ing_repo, prod_repo, cat_repo, job_repo)
        job = await importer.run()

        assert job.status == "completed"
        assert job.inserted_count == 2


class TestResume:
    async def test_resume_from_processed_rows(self, db_session: AsyncSession, tmp_path) -> None:
        csv_path = tmp_path / "off.csv"
        csv_path.write_text(OFF_CSV)
        ing_repo, prod_repo, cat_repo, job_repo = _make_repos(db_session)

        importer = OpenFoodFactsImporter(DatasetLoader(csv_path), ing_repo, prod_repo, cat_repo, job_repo)

        job = ImportJob(source="open_food_facts", file_path=str(csv_path), status="running", processed_rows=2)
        job_repo.add(job)
        await job_repo.flush()

        finished = await importer.run(job=job)
        assert finished.processed_rows == 3
        assert finished.inserted_count == 1
