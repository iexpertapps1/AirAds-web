# AirAd Backend

Hyperlocal vendor discovery platform — "Nearby + Now".

- **Phase A** — Internal Data Collection Portal: 7-role RBAC, vendor data collection, CSV import, GPS QA, field operations, audit trail
- **Phase B** — Full Public Platform: Customer/Vendor OTP auth, geospatial discovery/ranking, discount automation, voice bot, subscriptions, analytics

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 5.x + DRF 3.15 |
| Auth | SimpleJWT |
| Database | PostgreSQL 16 + PostGIS (GeoDjango) |
| Cache / Broker | Redis |
| Task Queue | Celery 5.x + Celery Beat |
| Validation | Pydantic v2 |
| API Docs | drf-spectacular (OpenAPI 3) |
| File Storage | AWS S3 via django-storages |
| Web Server | Gunicorn + Nginx |

---

## Prerequisites

- Docker ≥ 24 and Docker Compose v2
- Python 3.12 (for local development without Docker)
- `make` (optional, for convenience commands)

---

## Local Setup (Docker — Recommended)

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd airaad
cp .env.example .env
```

Edit `.env` and fill in all required values. See comments in `.env.example` for generation instructions.

**Generate `SECRET_KEY`:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Generate `ENCRYPTION_KEY` (32-byte AES-256 key, base64-encoded):**
```bash
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
```

### 2. Start the full stack

```bash
docker compose up --build -d
```

This starts: `postgres` (PostGIS), `redis`, `backend`, `celery-worker`, `celery-beat`, `frontend`, `nginx`.

### 3. Run migrations

```bash
docker compose exec backend python manage.py migrate
```

### 4. Seed reference data

```bash
docker compose exec backend python manage.py seed_data
```

Seeds: Countries, Cities (with GPS centroids), Areas, Landmarks, Tags (all 6 types), Subscription packages (SILVER/GOLD/DIAMOND/PLATINUM).

### 5. Create a superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

### 6. Access the application

| Service | URL |
|---|---|
| API | http://localhost/api/v1/ |
| OpenAPI Schema | http://localhost/api/v1/schema/ |
| Swagger UI | http://localhost/api/v1/docs/ |
| Health Check | http://localhost/api/v1/health/ |
| Frontend | http://localhost/ |

---

## Local Setup (Without Docker)

### 1. Install system dependencies

```bash
# macOS
brew install postgresql postgis gdal

# Ubuntu/Debian
sudo apt-get install -y postgresql postgis gdal-bin libgdal-dev libpq-dev
```

### 2. Create virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/development.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env — set DATABASE_URL, REDIS_URL, etc.
export DJANGO_SETTINGS_MODULE=config.settings.development
```

### 4. Run migrations and seed

```bash
python manage.py migrate
python manage.py seed_data
```

### 5. Start services

```bash
# Terminal 1 — Django dev server
python manage.py runserver

# Terminal 2 — Celery worker
celery -A celery_app worker --loglevel=info

# Terminal 3 — Celery Beat scheduler
celery -A celery_app beat --loglevel=info
```

---

## Running Tests

### Full test suite with coverage

```bash
docker compose exec backend pytest --cov=. --cov-fail-under=80 -v
```

### Specific test file or class

```bash
docker compose exec backend pytest tests/test_encryption.py -v
docker compose exec backend pytest tests/test_rbac.py::TestForRolesRBAC -v
```

### Without Docker

```bash
DJANGO_SETTINGS_MODULE=config.settings.test pytest --cov=. --cov-fail-under=80 -v
```

### Coverage report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

---

## Seed Data Command

The `seed_data` management command is **idempotent** — safe to run multiple times.

```bash
python manage.py seed_data
```

It seeds:
- Countries (with ISO-2 codes)
- Cities (with GPS centroids and bounding boxes)
- Areas (with parent hierarchy)
- Landmarks (≥3 aliases each)
- Tags (LOCATION, CATEGORY, INTENT, PROMOTION, TIME, SYSTEM types)
- Subscription packages (SILVER, GOLD, DIAMOND, PLATINUM)

Exit code `0` on success, `1` on error.

---

## Docker Commands Reference

```bash
# Start all services
docker compose up -d

# Rebuild and start
docker compose up --build -d

# View logs
docker compose logs -f backend
docker compose logs -f celery-worker

# Run Django management commands
docker compose exec backend python manage.py <command>

# Run migrations
docker compose exec backend python manage.py migrate

# Check for pending migrations (CI gate)
docker compose exec backend python manage.py migrate --check

# Validate OpenAPI schema
docker compose exec backend python manage.py spectacular --validate

# Stop all services
docker compose down

# Stop and remove volumes (full reset)
docker compose down -v
```

---

## Development Docker Override

For local development with hot-reload:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This mounts source code as volumes and uses Django's `runserver` + `npm run dev`.

---

## Environment Variables Reference

See `.env.example` for the full list with generation instructions. Key variables:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key — generate with `get_random_secret_key()` |
| `ENCRYPTION_KEY` | AES-256-GCM key — 32 bytes, base64-encoded |
| `DATABASE_URL` | PostgreSQL+PostGIS connection string |
| `REDIS_URL` | Redis connection string |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key for S3 |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key for S3 |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name |
| `CELERY_BROKER_URL` | Celery broker (typically same as `REDIS_URL`) |

---

## Project Structure

```
airaad/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py          # Shared settings
│   │   │   ├── production.py    # PostgreSQL, S3, DEBUG=False
│   │   │   ├── development.py   # Dev overrides
│   │   │   └── test.py          # CELERY_TASK_ALWAYS_EAGER=True
│   │   ├── urls.py
│   │   └── asgi.py
│   ├── celery_app.py
│   ├── apps/
│   │   ├── accounts/            # AdminUser, 7 roles, JWT, lockout
│   │   ├── geo/                 # Country, City, Area, Landmark
│   │   ├── vendors/             # Vendor, Discount, VoiceBotConfig
│   │   ├── tags/                # Tag taxonomy
│   │   ├── imports/             # ImportBatch, CSV engine
│   │   ├── field_ops/           # FieldVisit, FieldPhoto
│   │   ├── qa/                  # GPS drift, duplicate detection
│   │   ├── analytics/           # AnalyticsEvent, KPI endpoints
│   │   ├── audit/               # AuditLog, middleware, utils
│   │   ├── subscriptions/       # SubscriptionPackage (Phase B)
│   │   └── discovery/           # Search engine, voice search (Phase B)
│   └── core/
│       ├── encryption.py        # AES-256-GCM phone encryption
│       ├── geo_utils.py         # PostGIS ST_Distance wrappers
│       ├── middleware.py        # RequestIDMiddleware (FIRST)
│       ├── pagination.py        # StandardResultsPagination (25)
│       ├── exceptions.py        # custom_exception_handler
│       ├── storage.py           # S3 presigned URL helpers
│       ├── schemas.py           # Pydantic BusinessHoursSchema
│       └── utils.py             # get_client_ip, vendor_has_feature
├── frontend/
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
└── README.md
```

---

## Non-Negotiable Business Rules

| Rule | Description |
|---|---|
| R1 | PostGIS `ST_Distance(geography=True)` ONLY — never degree × constant |
| R2 | AES-256-GCM for all phone numbers at rest |
| R3 | `RolePermission.for_roles()` is the ONLY RBAC mechanism |
| R4 | All business logic in `services.py` — never in views or serializers |
| R5 | `AuditLog` on every POST/PATCH/DELETE — immutable, forever |
| R6 | Soft deletes only — `is_deleted=True`, never hard delete |
| R7 | `psycopg2` (compiled) in production — never `psycopg2-binary` |
| R8 | CSV content never passed over Celery broker — pass `batch_id` only |
| R9 | `error_log` in ImportBatch capped at 1000 entries |
| R10 | `celery-beat` replicas: 1 always |

---

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml` runs:

1. **Lint** — `flake8` + `black --check`
2. **Migration check** — `python manage.py migrate --check`
3. **Tests** — `pytest --cov-fail-under=80`
4. **Security scan** — `bandit` + `safety check`
5. **Frontend lint** — `eslint`
6. **Frontend build** — production build verification

All jobs must pass. No partial green.
