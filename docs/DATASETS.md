# Dataset sources and local setup

The backend contains importers for Open Food Facts and USDA FoodData Central. Runtime configuration points at these local files under `nutriscan_full_backup/backend/dataset/`:

- `en.openfoodfacts.org.products.csv.gz`
- `FoodData_Central_branded_food_csv_2026-04-30/FoodData_Central_branded_food_csv_2026-04-30/branded_food.csv`
- `FoodData_Central_Supporting_Data_csv_2022-10-28/`
- Small project lookup JSON files: `allergens.json`, `ingredient_aliases.json`, `ins_additives.json`

The large CSV/CSV.GZ source exports are intentionally ignored by Git. Keep the files locally and obtain them from the official project sources:

- [USDA FoodData Central downloads](https://fdc.nal.usda.gov/download-datasets/)
- [Open Food Facts data downloads](https://world.openfoodfacts.org/data)

Review current source licensing, attribution, and redistribution terms before downloading, importing, or redistributing data. This repository's MIT License applies to project code, not third-party datasets. The importer script is `nutriscan_full_backup/backend/scripts/import_food_datasets.py`. It has no `--help` mode: running `poetry run python -m scripts.import_food_datasets` immediately imports both configured sources into the configured database. Use a disposable/local database first.

The checked-in JSON lookup files are small and part of the project's configured runtime inputs. Confirm their provenance and any source-specific notices before redistributing changes to them.
