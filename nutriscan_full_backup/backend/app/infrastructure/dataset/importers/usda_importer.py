from __future__ import annotations

from app.infrastructure.dataset.importers.base_importer import BaseDatasetImporter, RowFields


class UsdaImporter(BaseDatasetImporter):
    """
    Expects USDA Branded Food CSV columns: fdc_id, description,
    brand_owner, branded_food_category, ingredients, gtin_upc.
    """

    source_name = "usda"

    def _extract_fields(self, row: dict[str, str]) -> RowFields | None:
        fdc_id = (row.get("fdc_id") or "").strip()
        name = (row.get("description") or "").strip()
        if not fdc_id or not name:
            return None

        return RowFields(
            external_id=fdc_id,
            name=name,
            category=(row.get("branded_food_category") or "").strip() or None,
            brand=(row.get("brand_owner") or "").strip() or None,
            barcode=(row.get("gtin_upc") or "").strip() or None,
            ingredients_text=(row.get("ingredients") or "").strip() or None,
        )
