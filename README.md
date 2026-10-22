# NutriScan AI

NutriScan is a Flutter application with a FastAPI backend for capturing food labels, extracting ingredient text, and evaluating ingredients against a user's saved allergy and health profile. The repository currently contains the project under `nutriscan_full_backup/`.

> **Health information:** NutriScan provides informational food-label analysis. OCR and rule-based results can be incomplete or incorrect and are not medical advice. Check the package label and consult a qualified professional for health decisions.

## Features

- Flutter app with Riverpod state management, GoRouter navigation, and Dio networking.
- User registration, login, refresh/logout, profile, allergy, and condition endpoints.
- Food-label image upload, scan lifecycle/history, notes, restore, cancellation, and scan statistics.
- PaddleOCR processing, ingredient text parsing, and ingredient/product/allergen/additive search backed by imported datasets.
- Rule-based product evaluation using stored profile, allergen, ingredient, and nutrition data; plus recommendation and history endpoints.
- PostgreSQL persistence through async SQLAlchemy and Alembic migrations.

Features depend on imported dataset content and configured services. The project does not claim a measured OCR or health-classification accuracy.

The current email adapter is development-only and does not deliver messages. The no-op virus scanner is restricted to development/test; uploads fail closed in other environment modes until a real scanner is configured.

## Tech stack

| Area | Technology |
| --- | --- |
| Mobile/client | Flutter, Dart, Riverpod, GoRouter, Dio |
| API | Python 3.12+, FastAPI, Pydantic |
| Database | PostgreSQL, SQLAlchemy 2, asyncpg, Alembic |
| Image/OCR | Pillow, OpenCV, PaddleOCR, PaddlePaddle |
| Tests | pytest, pytest-asyncio; Flutter test tooling |
| Python dependencies | Poetry |

## Architecture

```text
frontend (Flutter)
    └── HTTP / JSON ──> backend/app/api/v1 (FastAPI routes)
                          └── use_cases (application logic)
                               ├── domain (schemas and enums)
                               └── infrastructure (PostgreSQL, OCR, datasets,
                                   parsing, medical rules, recommendations)
```

The backend separates API routes, use cases, domain schemas, and infrastructure adapters. Alembic migrations define the PostgreSQL schema. The frontend is organized by app features with shared widgets and core configuration.

## Repository layout

```text
nutriscan_full_backup/
  backend/     FastAPI application, migrations, scripts, and tests
  frontend/    Flutter application and widget tests
docs/          Setup, API, and dataset notes
```

## Requirements

- Python 3.12 and Poetry
- Flutter SDK compatible with Dart `>=3.4.0 <4.0.0`
- PostgreSQL
- OpenSSL for creating a local RS256 keypair
- Optional source data files for dataset import; large third-party exports are intentionally excluded from Git

## Setup

### 1. Configure the backend

```powershell
cd nutriscan_full_backup/backend
poetry install
Copy-Item ..\..\.env.example .env
```

Edit `.env` with your local PostgreSQL connection. The example values are for local development only. Create a fresh keypair in `backend/keys/`:

```powershell
New-Item -ItemType Directory -Force keys | Out-Null
openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
```

Create the database, migrate, seed lookup data, and run the API:

```powershell
createdb nutriscan
poetry run alembic upgrade head
poetry run python -m scripts.seed
poetry run uvicorn app.main:app --reload --port 8000
```

The API health check is `http://localhost:8000/health`; interactive API docs are at `/docs` and `/redoc`.

### 2. Configure the Flutter app

In another terminal:

```powershell
cd nutriscan_full_backup/frontend
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

For Android emulator/device use, set `API_BASE_URL` to an address reachable from that device. The app's default base URL is `http://localhost:8000/api/v1`.

More details and troubleshooting are in [docs/SETUP.md](docs/SETUP.md).

## API documentation

The backend publishes OpenAPI at `/openapi.json` and interactive Swagger UI at `/docs` while running. Route groups, authentication expectations, and example calls are summarized in [docs/API.md](docs/API.md).

## Datasets

The backend has importers/configuration for Open Food Facts and USDA FoodData Central, as well as small JSON lookup data for allergens, aliases, and additives. Large source exports are excluded because of their size and third-party dataset terms; see [docs/DATASETS.md](docs/DATASETS.md) for sources, local paths, and import commands. Review each source's current terms before redistribution.

## Screenshots

Screenshots have not yet been added. Add reviewed, non-personal images under `docs/screenshots/` and link them here when available.

## Tests and checks

```powershell
cd nutriscan_full_backup/backend
poetry run pytest
cd ..\frontend
flutter test
flutter analyze
```

The backend suite is configured for pytest and includes an in-memory SQLite test dependency. OCR model downloads and PostgreSQL-backed testing require additional local setup.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md). Never commit `.env` files, credentials, private keys, database dumps, personal scan images, logs, OCR models, build output, or the excluded large dataset exports.

## License

The project code is released under the MIT License; third-party datasets and dependency licenses remain subject to their own terms. See [LICENSE](LICENSE).

## Future scope

Potential work includes adding privacy-safe screenshots, improving reproducible dataset setup, adding broader platform coverage, and measuring OCR/rule outcomes on a documented, rights-cleared evaluation set. These are future ideas, not current guarantees.
