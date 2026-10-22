# Local setup

See the root [README](../README.md) for the short setup path. This page records backend configuration details and common local setup requirements.

## Backend environment

Copy the root `.env.example` to `nutriscan_full_backup/backend/.env`. The backend loads `.env` relative to its working directory. Use local credentials and a fresh RS256 keypair; `.env` and PEM files are ignored by Git.

The `DATABASE_URL` uses `postgresql+asyncpg`; `DATABASE_URL_SYNC` is read by database tooling. Install PostgreSQL and create a database named `nutriscan` (or change both URLs). From the backend directory:

```powershell
poetry install
poetry run alembic upgrade head
poetry run python -m scripts.seed
poetry run uvicorn app.main:app --reload --port 8000
```

Dataset import is optional for starting the API but needed for dataset-backed search/evaluation. Follow [DATASETS.md](DATASETS.md).

## Flutter environment

From `nutriscan_full_backup/frontend`:

```powershell
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

The API URL is a Dart compile-time define. For a physical device or emulator, use a host address that the device can reach; `localhost` inside a device usually refers to that device.

## Useful URLs

- Health: `GET http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
