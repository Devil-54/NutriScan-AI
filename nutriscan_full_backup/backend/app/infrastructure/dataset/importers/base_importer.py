from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.logging import get_logger
from app.infrastructure.dataset.csv_loader import DatasetLoader
from app.infrastructure.db.models.category import Category
from app.infrastructure.db.models.food_product import FoodProduct, ProductIngredient
from app.infrastructure.db.models.ingredient import Ingredient
from app.infrastructure.db.models.import_job import ImportJob
from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.import_job_repository import ImportJobRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository
from app.infrastructure.knowledge_graph.normalizer import resolve_canonical_name

logger = get_logger()


@dataclass
class RowFields:
    external_id: str
    name: str
    category: str | None = None
    brand: str | None = None
    barcode: str | None = None
    ingredients_text: str | None = None


class BaseDatasetImporter(ABC):
    source_name: str = "unknown"

    def __init__(
        self,
        loader: DatasetLoader,
        ingredient_repo: IngredientRepository,
        product_repo: FoodProductRepository,
        category_repo: CategoryRepository,
        import_job_repo: ImportJobRepository,
    ) -> None:
        self.loader = loader
        self.ingredient_repo = ingredient_repo
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.import_job_repo = import_job_repo

    @abstractmethod
    def _extract_fields(self, row: dict[str, str]) -> RowFields | None:
        """Return None to skip a row that doesn't have enough usable data."""
        ...

    async def run(self, batch_size: int = 500, job: ImportJob | None = None) -> ImportJob:
        if job is None:
            job = ImportJob(source=self.source_name, file_path=str(self.loader.file_path), status="running")
            self.import_job_repo.add(job)
            await self.import_job_repo.flush()
        else:
            job.status = "running"

        logger.bind(event="IMPORT_STARTED", source=self.source_name, job_id=str(job.job_id)).info(
            "Dataset import started"
        )
        start = time.perf_counter()

        try:
            for batch in self.loader.stream_batches(batch_size=batch_size, skip_rows=job.processed_rows):
                for row in batch:
                    try:
                        fields = self._extract_fields(row)
                        if fields is None:
                            continue
                        await self._upsert_row(fields, job)
                    except Exception as exc:  # noqa: BLE001 - one bad row must not abort the whole import
                        job.error_count += 1
                        job.last_error = str(exc)[:2000]
                        logger.bind(event="IMPORT_ROW_ERROR", source=self.source_name).warning(str(exc))

                job.processed_rows += len(batch)
                await self.import_job_repo.commit()
                logger.bind(
                    event="IMPORT_PROGRESS",
                    source=self.source_name,
                    processed_rows=job.processed_rows,
                    inserted=job.inserted_count,
                    skipped=job.skipped_duplicate_count,
                ).info("Import batch committed")

            job.status = "completed"
        except FileNotFoundError as exc:
            job.status = "failed"
            job.last_error = str(exc)
            logger.bind(event="IMPORT_FAILED", source=self.source_name).error(str(exc))

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.bind(event="IMPORT_FINISHED", source=self.source_name, elapsed_ms=elapsed_ms, status=job.status).info(
            "Dataset import finished"
        )
        await self.import_job_repo.commit()
        return job

    async def _get_or_create_category(self, name: str | None) -> uuid.UUID | None:
        if not name:
            return None
        category = await self.category_repo.get_by_name(name)
        if category is None:
            category = Category(name=name)
            self.category_repo.add(category)
            await self.category_repo.flush()
        return category.category_id

    async def _upsert_row(self, fields: RowFields, job: ImportJob) -> None:
        existing = await self.ingredient_repo.get_by_source_external_id(self.source_name, fields.external_id)
        if existing is not None:
            job.skipped_duplicate_count += 1
            return

        category_id = await self._get_or_create_category(fields.category)
        canonical = resolve_canonical_name(fields.name)

        ingredient = await self.ingredient_repo.get_by_canonical_name(canonical)
        if ingredient is None:
            ingredient = Ingredient(
                canonical_name=canonical,
                category_id=category_id,
                source=self.source_name,
                external_id=fields.external_id,
            )
            self.ingredient_repo.add(ingredient)
            await self.ingredient_repo.flush()
            job.inserted_count += 1

        if fields.ingredients_text or fields.brand or fields.barcode:
            product = FoodProduct(
                name=fields.name,
                brand=fields.brand,
                barcode=fields.barcode,
                category_id=category_id,
                source=self.source_name,
                external_id=fields.external_id,
            )
            self.product_repo.add(product)
            await self.product_repo.flush()
            self.product_repo.add(
                ProductIngredient(product_id=product.product_id, ingredient_id=ingredient.ingredient_id)
            )
            await self.product_repo.flush()
