"""Small, label-specific post-processing for OCR output.

OCR remains responsible for reading the image; this only selects the parts of
that text which are meaningful to the analysis pipeline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LabelData:
    ingredients_text: str
    product_name: str | None
    brand: str | None
    category: str | None
    nutrition: dict[str, float | None]


_SECTION_END = re.compile(r"^(nutrition(?:al)? (?:facts|information)|allergen|contains|directions|storage|net\s*(?:wt|weight)|manufactured|best before)", re.I)
_PRODUCTS = (
    ("maggi", "Maggi", "Maggi", "Instant noodles"),
    ("lay's", "Lay's Chips", "Lay's", "Potato chips"),
    ("lays", "Lay's Chips", "Lay's", "Potato chips"),
    ("coca-cola", "Coca-Cola", "Coca-Cola", "Carbonated soft drink"),
    ("coca cola", "Coca-Cola", "Coca-Cola", "Carbonated soft drink"),
    ("quaker", "Quaker Oats", "Quaker", "Oats"),
)


def _number_after(text: str, names: tuple[str, ...]) -> float | None:
    for name in names:
        match = re.search(rf"{name}[^0-9]{{0,24}}(\d+(?:\.\d+)?)\s*(?:mg|g|kcal|cal)?", text, re.I)
        if match:
            return float(match.group(1))
    return None


def extract_label_data(text: str) -> LabelData:
    lines = [re.sub(r"\s+", " ", line).strip(" :-") for line in text.splitlines()]
    lines = [line for line in lines if line]
    joined = "\n".join(lines)

    ingredients = ""
    match = re.search(r"\bingredients?\s*[:\-]?\s*(.*)", joined, re.I)
    if match:
        collected = [match.group(1)] if match.group(1) else []
        start = joined[:match.start()].count("\n") + 1
        for line in lines[start: start + 12]:
            if _SECTION_END.match(line):
                break
            collected.append(line)
        ingredients = " ".join(collected).strip()
    # A label without an ingredients heading is better analysed as-is than
    # replaced with marketing copy; the parser still has its existing fallback.
    if not ingredients:
        ingredients = joined

    lower = joined.lower()
    product_name = brand = category = None
    for marker, name, product_brand, product_category in _PRODUCTS:
        if marker in lower:
            product_name, brand, category = name, product_brand, product_category
            break

    nutrition_text = joined
    nutrition = {
        "calories": _number_after(nutrition_text, ("energy", "calories")),
        "protein_g": _number_after(nutrition_text, ("protein",)),
        "sugar_g": _number_after(nutrition_text, ("total sugars?", "sugars?")),
        "fat_g": _number_after(nutrition_text, ("total fat", "fat")),
        "sodium_mg": _number_after(nutrition_text, ("sodium",)),
        "carbohydrates_g": _number_after(nutrition_text, ("total carbohydrates?", "carbohydrates?", "carbs?")),
    }
    return LabelData(ingredients, product_name, brand, category, nutrition)
