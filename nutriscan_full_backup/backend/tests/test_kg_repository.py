from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.additive import Additive
from app.infrastructure.db.models.allergen import Allergen
from app.infrastructure.db.models.food_product import FoodProduct
from app.infrastructure.db.models.ingredient import Ingredient
from app.infrastructure.db.repositories.additive_repository import AdditiveRepository
from app.infrastructure.db.repositories.allergen_repository import AllergenRepository
from app.infrastructure.db.repositories.food_product_repository import FoodProductRepository
from app.infrastructure.db.repositories.ingredient_repository import IngredientRepository

pytestmark = pytest.mark.asyncio


class TestIngredientRepository:
    async def test_search_by_canonical_name(self, db_session: AsyncSession) -> None:
        repo = IngredientRepository(db_session)
        repo.add(Ingredient(canonical_name="Sugar"))
        repo.add(Ingredient(canonical_name="Salt"))
        await db_session.commit()

        results = await repo.search("Sug")
        assert len(results) == 1
        assert results[0].canonical_name == "Sugar"

    async def test_search_by_alias(self, db_session: AsyncSession) -> None:
        repo = IngredientRepository(db_session)
        ing = Ingredient(canonical_name="Sugar")
        repo.add(ing)
        await db_session.flush()
        await repo.add_alias(ing.ingredient_id, "Sucrose")
        await db_session.commit()

        results = await repo.search_by_alias("Sucrose")
        assert len(results) == 1
        assert results[0].canonical_name == "Sugar"

    async def test_get_by_source_external_id_dedup(self, db_session: AsyncSession) -> None:
        repo = IngredientRepository(db_session)
        repo.add(Ingredient(canonical_name="Sugar", source="usda", external_id="123"))
        await db_session.commit()

        found = await repo.get_by_source_external_id("usda", "123")
        assert found is not None
        missing = await repo.get_by_source_external_id("usda", "999")
        assert missing is None


class TestAllergenRepository:
    async def test_search_and_link(self, db_session: AsyncSession) -> None:
        allergen_repo = AllergenRepository(db_session)
        ingredient_repo = IngredientRepository(db_session)

        allergen = Allergen(name="Peanut protein", category="legume")
        allergen_repo.add(allergen)
        ingredient = Ingredient(canonical_name="Peanut Butter")
        ingredient_repo.add(ingredient)
        await db_session.flush()

        await allergen_repo.link_ingredient(ingredient.ingredient_id, allergen.allergen_id)
        await db_session.commit()

        results = await allergen_repo.search("Peanut")
        assert len(results) == 1

        linked = await allergen_repo.get_allergens_for_ingredient(ingredient.ingredient_id)
        assert len(linked) == 1
        assert linked[0].name == "Peanut protein"


class TestAdditiveRepository:
    async def test_search_by_ins_code(self, db_session: AsyncSession) -> None:
        repo = AdditiveRepository(db_session)
        repo.add(Additive(ins_code="INS 322", common_name="Lecithin", purpose="Emulsifier", risk_category="low"))
        await db_session.commit()

        found = await repo.get_by_ins_code("INS 322")
        assert found is not None
        assert found.common_name == "Lecithin"

        results = await repo.search("Lecithin")
        assert len(results) == 1


class TestFoodProductRepository:
    async def test_search_by_name_and_barcode(self, db_session: AsyncSession) -> None:
        repo = FoodProductRepository(db_session)
        repo.add(FoodProduct(name="Choco Biscuit", brand="BrandX", barcode="8901234"))
        await db_session.commit()

        by_name = await repo.search("Choco")
        assert len(by_name) == 1

        by_barcode = await repo.search("8901234")
        assert len(by_barcode) == 1
