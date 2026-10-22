# NutriScan Backend

AI-Powered Personalized Food Safety & Ingredient Analysis System.

This FastAPI backend provides authentication and health profiles, food-label
uploads and history, OCR, ingredient parsing, dataset-backed search, rule-based
product evaluation, and recommendations. It uses PostgreSQL for application
data and Alembic for schema migrations. See the repository-root README for the
Flutter client and a high-level project overview.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Framework | FastAPI |
| Language | Python 3.12+ |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.x (async) |
| Validation | Pydantic v2 |
| Auth | JWT (RS256) + rotating refresh tokens |
| Password hashing | bcrypt |
| Migrations | Alembic |
| Dependency management | Poetry |
| Testing | Pytest + pytest-asyncio (SQLite in-memory for fast, isolated tests) |
| Logging | Loguru (structured JSON) |
| Rate limiting | slowapi |
| Image processing | Pillow (validation, corruption checks, thumbnails) |

---

## Project Structure

```
app/
├── api/v1/          # thin route controllers (auth, users, profile, scans) + shared deps
├── core/             # config, security (JWT/hashing), logging, exceptions
├── domain/            # enums + Pydantic schemas (framework-agnostic)
├── infrastructure/
│   ├── db/            # SQLAlchemy models, repositories, session
│   ├── email/           # email service interface (dev-mode logging implementation)
│   └── storage/          # StorageBackend (local, cloud-swappable), image validation,
│                            virus scan interface (placeholder), scan file path orchestration
├── middleware/         # logging, exceptions, rate limiting, security headers
├── use_cases/          # application/business logic (auth/*, profile/*, scans/*)
└── main.py             # app factory, wiring

migrations/              # Alembic (async-aware env.py)
scripts/seed.py           # seeds allergens + medical_conditions lookup tables
tests/                     # pytest suite
keys/                       # local RS256 keypair location (ignored by Git)
storage/uploads/              # local file storage root (created automatically; git-ignored)
```

---

## Installation

Requires Python 3.12+ and Poetry.

```powershell
poetry install
Copy-Item ..\..\.env.example .env
```

Edit `.env` and point `DATABASE_URL` / `DATABASE_URL_SYNC` at your local PostgreSQL instance.

### Generate a local RSA keypair

Create a local keypair under `keys/`; private key files are ignored by Git.
Never reuse a local development keypair in production:

```bash
openssl genrsa -out keys/private_key.pem 2048
openssl rsa -in keys/private_key.pem -pubout -out keys/public_key.pem
```

---

## Database Setup

```bash
# Create the database (adjust to your local Postgres setup)
createdb nutriscan

# Apply migrations
poetry run alembic upgrade head

# Seed allergen/medical-condition lookup tables (needed for /profile endpoints to validate against)
poetry run python -m scripts.seed
```

To generate a new migration after changing models:

```bash
poetry run alembic revision --autogenerate -m "describe your change"
poetry run alembic upgrade head
```

---

## Running the API

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

- API base: `http://localhost:8000/api/v1`
- Interactive docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

---

## Running Tests

Tests run against an in-memory SQLite database (via `aiosqlite`) so they need
no external services and stay fast/isolated. This is a test-only substitution —
production always targets PostgreSQL per the locked stack above.

```bash
poetry run pytest
poetry run pytest -v                  # verbose
poetry run pytest --cov=app           # with coverage, if pytest-cov is installed
```

---

## Environment Variables

See `.env.example` for the full list. Key ones:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Async Postgres connection string (asyncpg driver) |
| `DATABASE_URL_SYNC` | Sync connection string, used by tooling that needs sync access |
| `JWT_ALGORITHM` | Locked to `RS256` — asymmetric signing |
| `JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH` | Paths to the RSA keypair |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (default 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (default 7) |
| `CORS_ORIGINS` | Comma-separated allowlist of frontend origins |
| `RATE_LIMIT_DEFAULT` / `RATE_LIMIT_AUTH` | slowapi rate limit strings |

---

## API Overview (this phase)

All routes are prefixed with `/api/v1`.

**Authentication** (`/auth`): register, login, refresh, logout, forgot-password,
reset-password, change-password, verify-email.

**Users** (`/users`): get/deactivate own account (`/me`), admin-only paginated
listing (`GET /users`, requires `role=admin`).

**Profile** (`/profile`): get full profile (`/me`), update health profile
(BMI is always server-computed, never accepted from the client), replace
allergies (`/me/allergies`), replace medical conditions (`/me/conditions`).

**Food Scans** (`/scans`): upload a label image (`POST /upload`), paginated/filterable/searchable
history (`GET /history`), scan detail (`GET /{scan_id}`), lightweight status polling
(`GET /{scan_id}/status`), edit notes (`PATCH /{scan_id}`), soft delete (`DELETE /{scan_id}`),
restore (`POST /{scan_id}/restore`), cancel before processing starts (`POST /{scan_id}/cancel`),
plus two admin-only maintenance endpoints (`POST /admin/cleanup-expired`, `GET /admin/orphans`).

Every endpoint returns the standard envelope:
```json
{ "success": true, "data": { ... }, "meta": { ... } }
```
or on error:
```json
{ "success": false, "error": { "code": "SOME_CODE", "message": "..." } }
```

---

## Security Notes

- Access tokens are short-lived (15 min) and signed RS256; refresh tokens are
  opaque random strings, rotated on every use, and only their SHA-256 hash is
  ever persisted.
- Reuse of an already-revoked refresh token revokes **all** sessions for that
  user, as a theft-detection precaution.
- Password reset and change both revoke all existing sessions.
- Login failures return a generic error regardless of whether the email
  exists, to prevent account enumeration.
- All mutating actions are recorded in `audit_logs` (registration, login,
  logout, password changes, profile/allergy/condition updates, scan upload/
  delete/restore/cancel/metadata changes).

### Food Scan Infrastructure specifics

- **Image validation is content-based, not just extension-based**: every upload
  is actually decoded and format-verified with Pillow (`img.verify()`), not just
  checked by filename extension or client-supplied Content-Type header — this
  catches renamed/spoofed files and corrupted images alike.
- **Path traversal protection is structural**: on-disk paths are built from the
  server-generated `scan_id` (a UUID), never from the client's original
  filename, and `LocalStorageBackend._resolve()` additionally rejects any
  resolved path that would escape the configured storage root.
- **Duplicate protection** is per-user, based on SHA-256 checksum of file
  content — the same image re-uploaded by the same user is rejected; the same
  image uploaded by two different users is not a duplicate.
- **Virus scanning is a development placeholder** (`NoOpVirusScanner`) that
  always reports clean. Uploads are disabled outside development/test until
  a real scanner is configured through `get_virus_scanner()`.
- **Email delivery is not configured.** The development adapter only logs that
  a message was queued; it never logs recipient addresses or reset/verification
  tokens. Configure a real provider before relying on those flows operationally.
- **Soft delete + retention**: deleting a scan hides it from history and marks
  it deleted but keeps files in place so it can be restored; permanent file
  removal happens through the expiration/cleanup maintenance path
  (`POST /scans/admin/cleanup-expired`), not at delete time.

---

## Current limitations

- OCR currently runs through the configured PaddleOCR engine; it is not an
  asynchronous worker queue.
- Medical evaluation is rule-based and depends on profile values and imported
  dataset content. It is informational, not a diagnosis.
- No LLM narrative service is configured.
- Email delivery is not configured. Password reset and verification messages
  are not sent by the development logging adapter.
- A real virus scanner is not configured. Uploads are disabled outside
  development/test until one is provided.
