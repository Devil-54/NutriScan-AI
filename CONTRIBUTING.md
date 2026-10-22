# Contributing

Thanks for considering a contribution to NutriScan.

## Before you start

- Check existing issues and discussions for related work.
- For substantial changes, open an issue first to agree on scope.
- Keep changes focused and describe user-visible behavior, migration needs, and limitations.
- Do not include real user data, credentials, private keys, database dumps, OCR uploads, or large source dataset exports.

## Development checks

Backend (from `nutriscan_full_backup/backend`):

```powershell
poetry install
poetry run pytest
```

Frontend (from `nutriscan_full_backup/frontend`):

```powershell
flutter pub get
flutter analyze
flutter test
```

Database changes should include an Alembic migration. Keep API changes reflected in FastAPI's generated OpenAPI schema and update `docs/API.md` when route behavior changes.

## Pull requests

1. Create a focused branch from `main`.
2. Make the change and add or update tests where appropriate.
3. Run relevant checks and report their results, including any that could not run.
4. Open a pull request with a clear summary, motivation, test results, and screenshots for UI changes when useful.

By submitting a contribution, you agree that it may be distributed under the repository's MIT License, subject to third-party content retaining its own license terms.
