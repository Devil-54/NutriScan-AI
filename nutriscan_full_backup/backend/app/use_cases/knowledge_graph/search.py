from __future__ import annotations

from app.domain.schemas.knowledge_graph import (
    AdditiveSearchResult,
    AllergenSearchResult,
    IngredientSearchResult,
    ProductSearchResult,
)
from app.infrastructure.db.repositories.additive_repository import AdditiveRepository
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository


class SearchIngredientUseCase:
    def __init__(self, ingredient_repo: IngredientRepository) -> None:
        self.ingredient_repo = ingredient_repo

    async def execute(self, query: str, limit: int = 20) -> list[IngredientSearchResult]:
        by_name = await self.ingredient_repo.search(query, limit)
        by_alias = await self.ingredient_repo.search_by_alias(query, limit)
        seen: set = set()
        merged = []
        for ing in [*by_name, *by_alias]:
            if ing.ingredient_id in seen:
                continue
            seen.add(ing.ingredient_id)
            merged.append(ing)
        return [IngredientSearchResult.model_validate(i) for i in merged[:limit]]


class SearchProductUseCase:
    def __init__(self, product_repo: FoodProductRepository) -> None:
        self.product_repo = product_repo

    async def execute(self, query: str, limit: int = 20) -> list[ProductSearchResult]:
        rows = await self.product_repo.search(query, limit)
        return [ProductSearchResult.model_validate(r) for r in rows]


class SearchAllergenUseCase:
    def __init__(self, allergen_repo: AllergenRepository) -> None:
        self.allergen_repo = allergen_repo

    async def execute(self, query: str, limit: int = 20) -> list[AllergenSearchResult]:
        rows = await self.allergen_repo.search(query, limit)
        return [AllergenSearchResult.model_validate(r) for r in rows]


class SearchAdditiveUseCase:
    def __init__(self, additive_repo: AdditiveRepository) -> None:
        self.additive_repo = additive_repo

    async def execute(self, query: str, limit: int = 20) -> list[AdditiveSearchResult]:
        rows = await self.additive_repo.search(query, limit)
        return [AdditiveSearchResult.model_validate(r) for r in rows]
