"""Load the checked-in JSON knowledge-graph datasets and medical lookups.

Run with: ``poetry run python -m scripts.seed``.
"""
import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.infrastructure.db.models.additive import Additive
from app.infrastructure.db.models.allergen import Allergen
from app.infrastructure.db.models.ingredient import Ingredient, IngredientAlias
from app.infrastructure.db.models.ingredient_allergen import IngredientAllergen
from app.infrastructure.db.models.medical_condition import MedicalCondition
from app.infrastructure.db.session import AsyncSessionLocal

ALLERGENS = [
    ("Peanut protein", "legume"),
    ("Tree nut protein", "nut"),
    ("Dairy protein (casein/whey)", "dairy"),
    ("Gluten", "grain"),
    ("Egg protein", "egg"),
    ("Soy protein", "legume"),
    ("Shellfish protein", "seafood"),
    ("Fish protein", "seafood"),
    ("Sesame protein", "seed"),
    ("Mustard", "seed"),
]

MEDICAL_CONDITIONS = [
    ("Type 2 Diabetes", "metabolic"),
    ("Type 1 Diabetes", "metabolic"),
    ("Prediabetes", "metabolic"),
    ("Hypertension", "cardiovascular"),
    ("Chronic Kidney Disease", "renal"),
    ("Coronary Heart Disease", "cardiovascular"),
    ("Celiac Disease", "autoimmune"),
    ("Lactose Intolerance", "digestive"),
    ("Obesity", "metabolic"),
    ("High Cholesterol", "cardiovascular"),
    ("Liver Disease", "hepatic"),
    ("PCOS", "endocrine"),
    ("Thyroid Disorder", "endocrine"),
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        summary = {"allergens": 0, "ingredient_aliases": 0, "additives": 0, "medical_conditions": 0}

        allergens = _read_json(settings.ALLERGENS_DATASET_PATH)
        for item in allergens:
            name = item["ingredient"].strip()
            allergen = await session.scalar(select(Allergen).where(Allergen.name == name))
            if allergen is None:
                allergen = Allergen(name=name, category=item.get("risk_level"))
                session.add(allergen)
                await session.flush()
                summary["allergens"] += 1

            ingredient = await session.scalar(select(Ingredient).where(Ingredient.canonical_name == name))
            if ingredient is None:
                ingredient = Ingredient(canonical_name=name, description=item.get("description"), source="allergens_json", external_id=name)
                session.add(ingredient)
                await session.flush()
            linked = await session.scalar(
                select(IngredientAllergen).where(
                    IngredientAllergen.ingredient_id == ingredient.ingredient_id,
                    IngredientAllergen.allergen_id == allergen.allergen_id,
                )
            )
            if linked is None:
                session.add(IngredientAllergen(ingredient_id=ingredient.ingredient_id, allergen_id=allergen.allergen_id))

            for alias_text in item.get("aliases", []):
                alias = alias_text.strip()
                if alias and await session.scalar(
                    select(IngredientAlias).where(
                        IngredientAlias.ingredient_id == ingredient.ingredient_id,
                        IngredientAlias.alias_text == alias,
                    )
                ) is None:
                    session.add(IngredientAlias(ingredient_id=ingredient.ingredient_id, alias_text=alias, alias_type="allergen_alias"))

        for item in _read_json(settings.INGREDIENT_ALIASES_DATASET_PATH):
            name = item["standard_name"].strip()
            ingredient = await session.scalar(select(Ingredient).where(Ingredient.canonical_name == name))
            if ingredient is None:
                ingredient = Ingredient(canonical_name=name, source="ingredient_aliases_json", external_id=name)
                session.add(ingredient)
                await session.flush()
            for alias_text in item.get("aliases", []):
                alias = alias_text.strip()
                if alias and await session.scalar(
                    select(IngredientAlias).where(
                        IngredientAlias.ingredient_id == ingredient.ingredient_id,
                        IngredientAlias.alias_text == alias,
                    )
                ) is None:
                    session.add(IngredientAlias(ingredient_id=ingredient.ingredient_id, alias_text=alias))
                    summary["ingredient_aliases"] += 1

        for item in _read_json(settings.INS_ADDITIVES_DATASET_PATH):
            code = item["ins_code"].strip()
            if await session.scalar(select(Additive).where(Additive.ins_code == code)) is None:
                session.add(
                    Additive(
                        ins_code=code,
                        common_name=item["name"].strip(),
                        purpose=item.get("purpose"),
                        risk_category=item.get("risk_level"),
                    )
                )
                summary["additives"] += 1

        for name, category in ALLERGENS:
            if await session.scalar(select(Allergen).where(Allergen.name == name)) is None:
                session.add(Allergen(name=name, category=category))
        for name, category in MEDICAL_CONDITIONS:
            if await session.scalar(select(MedicalCondition).where(MedicalCondition.name == name)) is None:
                session.add(MedicalCondition(name=name, category=category))
                summary["medical_conditions"] += 1
        await session.commit()
    print("Imported JSON datasets:", summary)


def _read_json(path: str) -> list[dict]:
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    return json.loads(dataset_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    asyncio.run(seed())
