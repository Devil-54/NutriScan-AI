from __future__ import annotations

from app.infrastructure.dataset.importers.base_importer import BaseDatasetImporter, RowFields


class OpenFoodFactsImporter(BaseDatasetImporter):
    """
    Expects Open Food Facts export CSV columns (tab or comma separated,
    configured via DatasetLoader): code, product_name, brands,
    categories, ingredients_text. Missing/malformed rows are skipped, not
    fatal - the import continues (see BaseDatasetImporter.run).
    """

    source_name = "open_food_facts"

    def _extract_fields(self, row: dict[str, str]) -> RowFields | None:
        code = (row.get("code") or "").strip()
        name = (row.get("product_name") or "").strip()
        if not code or not name:
            return None

        category = (row.get("categories") or "").split(",")[0].strip() or None
        return RowFields(
            external_id=code,
            name=name,
            category=category,
            brand=(row.get("brands") or "").split(",")[0].strip() or None,
            barcode=code,
            ingredients_text=(row.get("ingredients_text") or "").strip() or None,
        )
