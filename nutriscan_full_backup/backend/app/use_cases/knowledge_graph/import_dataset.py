from __future__ import annotations

from app.core.exceptions import ValidationException
from app.domain.schemas.knowledge_graph import ImportDatasetRequest, ImportJobRead
from app.infrastructure.dataset.csv_loader import DatasetLoader
from app.infrastructure.dataset.importers.open_food_facts_importer import OpenFoodFactsImporter
from app.infrastructure.dataset.importers.usda_importer import UsdaImporter
from app.infrastructure.db.repositories.category_repository import CategoryRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.import_job_repository import ImportJobRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository

_IMPORTERS = {"open_food_facts": OpenFoodFactsImporter, "usda": UsdaImporter}


class ImportDatasetUseCase:
    def __init__(
        self,
        ingredient_repo: IngredientRepository,
        product_repo: FoodProductRepository,
        category_repo: CategoryRepository,
        import_job_repo: ImportJobRepository,
    ) -> None:
        self.ingredient_repo = ingredient_repo
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.import_job_repo = import_job_repo

    async def execute(self, payload: ImportDatasetRequest) -> ImportJobRead:
        importer_cls = _IMPORTERS.get(payload.source)
        if importer_cls is None:
            raise ValidationException(f"Unsupported dataset source: {payload.source}", error_code="UNSUPPORTED_SOURCE")

        loader = DatasetLoader(payload.file_path)
        importer = importer_cls(loader, self.ingredient_repo, self.product_repo, self.category_repo, self.import_job_repo)
        job = await importer.run(batch_size=payload.batch_size)
        return ImportJobRead.model_validate(job)
