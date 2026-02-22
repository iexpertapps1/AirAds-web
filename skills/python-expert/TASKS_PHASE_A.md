# AirAd Backend — Python Expert Task List: PHASE A
## Source: `plans/01_BACKEND_PLAN.md` — Steps 1–31
### Priority Order: Correctness → Type Safety → Performance → Style
### Gate: All tasks must pass `docker-compose up` + `pytest --cov-fail-under=80` before Phase B begins

---

## SESSION A-S1 — Infrastructure (Steps 1–4)

### TASK-001 — `.env.example` + `README.md`
**Plan Ref:** Step 1 | **Priority:** CRITICAL | **Effort:** XS

- [ ] Zero literal placeholder values — only generation instructions
- [ ] `ENCRYPTION_KEY`: 32-byte base64 generation command documented
- [ ] All vars: `SECRET_KEY`, `ENCRYPTION_KEY`, `DATABASE_URL`, `REDIS_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`
- [ ] `README.md`: local setup, Docker setup, test commands, seed data command

---

### TASK-002 — `docker-compose.yml` + `docker-compose.dev.yml`
**Plan Ref:** Step 2 | **Priority:** CRITICAL | **Effort:** S

- [ ] Services: `postgres` (PostGIS image), `redis`, `backend`, `celery-worker`, `celery-beat`, `frontend`, `nginx`
- [ ] `celery-beat`: `deploy.replicas: 1` — exactly one, always
- [ ] No source code volume mounts in production
- [ ] Health checks: `pg_isready` (postgres), `redis-cli ping` (redis)
- [ ] Backend NOT directly port-exposed — nginx reverse proxy only
- [ ] Dev override: source mounts, `runserver`, `npm run dev`

---

### TASK-003 — Dockerfiles
**Plan Ref:** Step 3 | **Priority:** CRITICAL | **Effort:** S

- [ ] Backend Stage 1 (builder): `python:3.12-slim`, compile `psycopg2` from source — **NOT** `psycopg2-binary`
- [ ] Backend Stage 2: `python:3.12-slim` + GDAL pinned to match PostGIS image exactly
- [ ] CMD: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4`
- [ ] Frontend: `node:20-alpine` build → `nginx:alpine` serve (never `npm run dev` in production)

> ⚠️ GDAL version mismatch with PostGIS causes silent GeoDjango failures — pin explicitly.

---

### TASK-004 — `nginx/nginx.conf`
**Plan Ref:** Step 4 | **Priority:** HIGH | **Effort:** XS

- [ ] `/api/` → `backend:8000`
- [ ] `/` → `frontend:80`
- [ ] No direct backend port exposure

---

## SESSION A-S2 — Requirements, Settings, Celery, Core (Steps 5–9)

### TASK-005 — `requirements/` files
**Plan Ref:** Step 5 | **Priority:** CRITICAL | **Effort:** XS

- [ ] `base.txt`: Django 5.x, DRF 3.15, SimpleJWT, drf-spectacular, django-environ, Pydantic, Celery 5.x, redis, django-storages, boto3
- [ ] `production.txt`: base + `psycopg2` (compiled) + gunicorn — **NEVER `psycopg2-binary`**
- [ ] `development.txt`: base + `psycopg2-binary` + django-extensions + ipython
- [ ] `test.txt`: development + pytest-django + factory_boy + moto + freezegun + coverage

---

### TASK-006 — `config/settings/`
**Plan Ref:** Step 6 | **Priority:** CRITICAL | **Effort:** S

- [ ] `base.py`: `ENGINE: django.contrib.gis.db.backends.postgis` (GeoDjango — mandatory)
- [ ] `base.py`: `CONN_MAX_AGE: 60`
- [ ] `base.py`: `SIMPLE_JWT` — `ACCESS=15min`, `REFRESH=7days`, `ROTATE_REFRESH_TOKENS=True`
- [ ] `base.py`: `EXCEPTION_HANDLER: core.exceptions.custom_exception_handler`
- [ ] `base.py`: `RequestIDMiddleware` is **index 0** in `MIDDLEWARE` list
- [ ] `base.py`: `DEFAULT_PAGINATION_CLASS: core.pagination.StandardResultsPagination`
- [ ] `production.py`: PostgreSQL, S3 storage, `DEBUG=False`
- [ ] `development.py`: local DB, `DEBUG=True`
- [ ] `test.py`: test DB, `CELERY_TASK_ALWAYS_EAGER=True`, dummy AWS vars

> ⚠️ Use `django-environ` `env()` for all secrets — never hardcode. `MIDDLEWARE` order is security-critical.

---

### TASK-007 — `config/urls.py`
**Plan Ref:** Step 7 | **Priority:** HIGH | **Effort:** XS

- [ ] All prefixes: `/api/v1/auth/`, `/api/v1/geo/`, `/api/v1/tags/`, `/api/v1/vendors/`, `/api/v1/imports/`, `/api/v1/field-ops/`, `/api/v1/qa/`, `/api/v1/analytics/`, `/api/v1/audit/`, `/api/v1/health/`, `/api/v1/schema/`, `/api/v1/docs/`

---

### TASK-008 — `celery_app.py`
**Plan Ref:** Step 8 | **Priority:** CRITICAL | **Effort:** S

- [ ] Celery app instance with `autodiscover_tasks()`
- [ ] `setup_periodic_tasks()` via `@app.on_after_finalize.connect` — all schedules in code, not DB:
  - `weekly_gps_drift_scan`: Sunday 02:00 UTC
  - `daily_duplicate_scan`: daily 03:00 UTC
  - `discount_scheduler`: every 1 minute (Phase B — register now)
  - `subscription_expiry_check`: daily midnight UTC (Phase B)
  - `hourly_tag_assignment`: every 1 hour (Phase B)
- [ ] `task_failure` signal handler: structured log with task name, args, exception

> ⚠️ Type hint signal handler: `def on_task_failure(sender, task_id: str, exception: Exception, **kwargs: Any) -> None`. Use structured logging — not `print`.

---

### TASK-009 — `core/` utilities
**Plan Ref:** Step 9 | **Priority:** CRITICAL | **Effort:** M

**009a — `core/encryption.py`**
- [ ] `encrypt(plaintext: str) -> bytes` — AES-256-GCM, randomised IV per call (use `cryptography.hazmat.primitives.ciphers.aead.AESGCM`)
- [ ] `decrypt(ciphertext: bytes) -> str`
- [ ] Empty string → returns empty bytes (not an error)
- [ ] Key from `settings.ENCRYPTION_KEY` (base64-decoded 32 bytes)
- [ ] Raise specific `EncryptionError` — no bare `except`

**009b — `core/geo_utils.py`**
- [ ] `calculate_drift_distance(point_a: Point, point_b: Point) -> float` — `ST_Distance(geography=True)` ONLY
- [ ] `find_nearby_vendors(center: Point, radius_meters: float) -> QuerySet` — `ST_DWithin` ONLY
- [ ] **NEVER** degree × constant — non-negotiable rule R1

**009c — `core/middleware.py`**
- [ ] `RequestIDMiddleware`: `uuid.uuid4()` per request, `X-Request-ID` header, `request.request_id`
- [ ] Must be FIRST middleware

> ⚠️ Use `uuid.uuid4()` — not `uuid.uuid1()` (privacy risk).

**009d — `core/pagination.py`**
- [ ] `StandardResultsPagination(PageNumberPagination)`: `PAGE_SIZE=25`, `max_page_size=100`

**009e — `core/exceptions.py`**
- [ ] `custom_exception_handler(exc, context)` → wraps all DRF exceptions into `{success, data, message, errors}` envelope
- [ ] Call DRF's `exception_handler` first, then wrap — never swallow unhandled exceptions

**009f — `core/schemas.py`**
- [ ] `BusinessHoursSchema(BaseModel)` — Pydantic v2
- [ ] 7 day keys `MON`–`SUN`, each: `{open: "HH:MM", close: "HH:MM", is_closed: bool}`
- [ ] Called in `vendors/services.py` on every write

**009g — `core/storage.py`**
- [ ] `generate_presigned_url(key: str, expiry: int = 3600) -> str`
- [ ] `upload_file_to_s3(file: IO, prefix: str) -> str` — returns S3 key only, never public URL

**009h — `core/utils.py`**
- [ ] `get_client_ip(request: HttpRequest) -> str` — handles `X-Forwarded-For`
- [ ] `vendor_has_feature(vendor: "Vendor", feature: str) -> bool` — stub returning `False` (Phase B)

---

## SESSION A-S3 — Accounts + Permissions + Auth + Audit (Steps 10–13)

### TASK-010 — `apps/accounts/models.py`
**Plan Ref:** Step 10 | **Priority:** CRITICAL | **Effort:** S

- [ ] `AdminUser(AbstractBaseUser)`: `id(UUIDField PK, default=uuid.uuid4)`, `email(unique)`, `full_name`, `role(7 TextChoices)`, `is_active`, `failed_login_count(default=0)`, `locked_until(null=True)`, `last_login_ip`, `created_at(auto_now_add)`, `updated_at(auto_now)`
- [ ] `AdminRole` as `models.TextChoices` — all 7 roles defined
- [ ] `USERNAME_FIELD = 'email'`
- [ ] Custom `AdminUserManager` with `create_user` and `create_superuser` — fully type-hinted

> ⚠️ `default=uuid.uuid4` (callable) — NOT `default=uuid.uuid4()` (mutable default bug).

---

### TASK-011 — `apps/accounts/permissions.py`
**Plan Ref:** Step 11 | **Priority:** CRITICAL | **Effort:** XS

- [ ] `RolePermission(BasePermission)` with `allowed_roles: tuple[AdminRole, ...]`
- [ ] `for_roles(*roles: AdminRole) -> type["RolePermission"]` classmethod using `type()` factory
- [ ] `has_permission`: checks `is_authenticated` AND `role in self.allowed_roles`
- [ ] No `__call__` method — class-based only
- [ ] **Every view** uses `RolePermission.for_roles(...)` — no exceptions

---

### TASK-012 — Auth views + serializers + URLs
**Plan Ref:** Step 12 | **Priority:** CRITICAL | **Effort:** M

- [ ] Login: lockout check BEFORE password verify (5 failures → 429 + `Retry-After`, `locked_until = now() + 15min`)
- [ ] On success: reset `failed_login_count = 0`, update `last_login_ip`
- [ ] JWT custom serializer adds `role`, `full_name`, `email` to claims
- [ ] All auth events → `AuditLog` entry
- [ ] Endpoints: `POST /api/v1/auth/login/`, `POST /api/v1/auth/refresh/`, `POST /api/v1/auth/logout/`

> ⚠️ Use `django.utils.timezone.now()` — never `datetime.now()`. Explicit `except AdminUser.DoesNotExist` — no bare `except`.

---

### TASK-013 — `apps/audit/models.py` + utils
**Plan Ref:** Step 13 | **Priority:** CRITICAL | **Effort:** S

- [ ] `AuditLog`: `id(UUID)`, `action(db_index=True)`, `actor(FK null=True, SET_NULL)`, `actor_label(email snapshot)`, `target_type`, `target_id(UUID null=True)`, `before_state(JSON)`, `after_state(JSON)`, `request_id`, `ip_address`, `created_at(db_index=True)`
- [ ] Composite indexes: `(target_type, target_id)`, `(actor, created_at)`
- [ ] IMMUTABLE — custom manager overrides `update()` to raise `NotImplementedError`
- [ ] `log_action(action: str, actor: AdminUser | None, target_obj: Model | None, request: HttpRequest, before: dict, after: dict) -> AuditLog` in `apps/audit/utils.py`
- [ ] Called explicitly from `services.py` only — never via signals

---

## SESSION A-S4 — Geo + Tags + Vendors + Imports Models (Steps 14–17)

### TASK-014 — `apps/geo/models.py` + migrations
**Plan Ref:** Step 14 | **Priority:** CRITICAL | **Effort:** M

- [ ] `Country`, `City`, `Area`, `Landmark` — all fields per plan spec
- [ ] ALL `PointField` columns: GiST index via `migrations.RunSQL` — NOT `models.Index`
- [ ] GiST SQL: `CREATE INDEX IF NOT EXISTS <name> ON <table> USING GiST (<col>);`
- [ ] `JSONField(default=list)` — callable, not `[]` (mutable default rule)
- [ ] `slug` immutability enforced in `geo/services.py` — raise `ValidationError` if update attempted

---

### TASK-015 — `apps/tags/models.py`
**Plan Ref:** Step 15 | **Priority:** HIGH | **Effort:** XS

- [ ] `Tag`: `id(UUID)`, `name`, `slug(immutable)`, `tag_type(TextChoices: LOCATION/CATEGORY/INTENT/PROMOTION/TIME/SYSTEM)`, `display_label`, `display_order`, `icon_name`, `is_active`, `created_at`
- [ ] `SYSTEM` tags: API rejects create/edit/delete — enforced in `tags/services.py`

---

### TASK-016 — `apps/vendors/models.py`
**Plan Ref:** Step 16 | **Priority:** CRITICAL | **Effort:** M

- [ ] `phone_number_encrypted(BinaryField)` — AES-256-GCM, never plaintext
- [ ] `business_hours(JSONField)` — validated via `BusinessHoursSchema` on every write (in services)
- [ ] `qc_reviewed_by(FK AdminUser null=True)` — FK, NOT raw UUID
- [ ] `gps_point(PointField)` — GiST index via `migrations.RunSQL`
- [ ] `is_deleted(BooleanField default=False, db_index=True)` — soft delete only
- [ ] Composite indexes: `(qc_status, is_deleted)`, `(area, is_deleted)`, `(data_source)`
- [ ] `qc_status` TextChoices: `PENDING/APPROVED/REJECTED/NEEDS_REVIEW`
- [ ] `data_source` TextChoices: `CSV_IMPORT/GOOGLE_PLACES/MANUAL_ENTRY/FIELD_AGENT`
- [ ] Default manager filters `is_deleted=False` automatically
- [ ] `delete()` overridden → sets `is_deleted=True`, calls `save()` — never `super().delete()`

---

### TASK-017 — `apps/imports/models.py` + `apps/field_ops/models.py`
**Plan Ref:** Step 17 | **Priority:** HIGH | **Effort:** S

- [ ] `ImportBatch`: `file_key(CharField — S3 key ONLY)`, `status(QUEUED/PROCESSING/DONE/FAILED)`, `error_log(JSONField default=list)`, `created_by(FK AdminUser)`
- [ ] `FieldVisit`: `vendor(FK)`, `agent(FK AdminUser)`, `gps_confirmed_point(PointField null=True)`
- [ ] `FieldPhoto`: `s3_key(CharField)` — presigned URL generated on read, never stored as public URL
- [ ] `error_log` 1000-entry cap enforced in `imports/services.py` — not at model level

---

## SESSION A-S5 — Services, Serializers, Views (Steps 18–20)

### TASK-018 — All `services.py` files
**Plan Ref:** Step 18 | **Priority:** CRITICAL | **Effort:** L

**Apps:** `accounts`, `geo`, `tags`, `vendors`, `imports`, `field_ops`, `qa`, `analytics`

**Standards for ALL services:**
- [ ] ALL domain logic in `services.py` — zero logic in views or serializers
- [ ] Every mutation calls `log_action()` from `apps/audit/utils.py`
- [ ] Full type hints + Google-style docstrings on all functions
- [ ] Specific exception handling — no bare `except`
- [ ] No mutable default arguments
- [ ] Multi-step mutations wrapped in `@transaction.atomic`

**Key functions:**
- `accounts/services.py`: `authenticate_user()`, `create_admin_user()`
- `vendors/services.py`: `create_vendor()`, `update_vendor()`, `soft_delete_vendor()`, `update_qc_status()` — phone encrypt/decrypt here, `BusinessHoursSchema` validation here
- `imports/services.py`: `create_import_batch()` (upload to S3, store key only, dispatch task), `append_error_log()` (enforce 1000-cap)
- `geo/services.py`: `create_city()`, slug immutability enforcement

---

### TASK-019 — All DRF serializers
**Plan Ref:** Step 19 | **Priority:** HIGH | **Effort:** M

- [ ] `VendorSerializer`: phone decrypted on `to_representation`, encrypted on write
- [ ] GPS: accept `latitude`/`longitude` floats → `Point(longitude, latitude)` in `validate()`
- [ ] No business logic in serializers — validation only, delegate to services
- [ ] `read_only_fields` explicitly declared on all serializers

> ⚠️ `Point(longitude, latitude)` — lon/lat order, not lat/lon. Wrap decrypt in `try/except EncryptionError`.

---

### TASK-020 — All DRF views + ViewSets + URLs
**Plan Ref:** Step 20 | **Priority:** CRITICAL | **Effort:** M

- [ ] Every view: `permission_classes = [RolePermission.for_roles(...)]` — no exceptions
- [ ] Zero business logic in views — all delegated to `services.py`
- [ ] All views: `@extend_schema(tags=[...], summary="...", responses={...})`
- [ ] All viewsets: `StandardResultsPagination`
- [ ] `get_queryset()` always filters `is_deleted=False` for soft-delete models

---

## SESSION A-S6 — Import/QA Tasks + Health Check (Steps 21–23)

### TASK-021 — `apps/imports/tasks.py`
**Plan Ref:** Step 21 | **Priority:** CRITICAL | **Effort:** M

- [ ] `@shared_task(bind=True, max_retries=3)` — `def process_import_batch(self, batch_id: str) -> None`
- [ ] Idempotency: `if batch.status == 'PROCESSING': return`
- [ ] Read CSV from S3 via `boto3` `StreamingBody` — **NEVER** from broker payload
- [ ] Per-row: validate → append error (cap 1000) → continue (never abort batch)
- [ ] On row success: `Vendor(data_source=CSV_IMPORT)`
- [ ] Retry: `countdown=2**self.request.retries * 60`
- [ ] `processed_rows` and `error_count` updated per row

> ⚠️ Use context manager for `StreamingBody`. Never download full CSV to memory.

---

### TASK-022 — `apps/qa/tasks.py`
**Plan Ref:** Step 22 | **Priority:** HIGH | **Effort:** M

**`weekly_gps_drift_scan` (Sunday 02:00 UTC):**
- [ ] `ST_Distance(geography=True) > 20m` → `qc_status = NEEDS_REVIEW` + `AuditLog` per vendor

**`daily_duplicate_scan` (daily 03:00 UTC):**
- [ ] `ST_DWithin` 50m + `difflib.SequenceMatcher(ratio >= 0.85)` on `business_name`
- [ ] Flag duplicates → `qc_status = NEEDS_REVIEW`
- [ ] Cap: 100 comparisons per vendor

> ⚠️ `difflib` is stdlib. Always filter `is_deleted=False`. Batch DB queries — avoid N+1.

---

### TASK-023 — `GET /api/v1/health/`
**Plan Ref:** Step 23 | **Priority:** HIGH | **Effort:** XS

- [ ] Unauthenticated endpoint
- [ ] DB: `SELECT 1` in `try/except OperationalError`
- [ ] Redis: ping in `try/except redis.exceptions.ConnectionError`
- [ ] `200 {"status": "healthy"}` / `503 {"status": "degraded", "details": {...}}`
- [ ] Never raises unhandled exception

---

## SESSION A-S7 — Schemas + Seed Data + OpenAPI (Steps 24–26)

### TASK-024 — `core/schemas.py` — `BusinessHoursSchema`
**Plan Ref:** Step 24 | **Priority:** CRITICAL | **Effort:** XS

- [ ] Pydantic v2 `BaseModel`
- [ ] 7 day keys: `MON`, `TUE`, `WED`, `THU`, `FRI`, `SAT`, `SUN`
- [ ] Each day: `{open: "HH:MM", close: "HH:MM", is_closed: bool}`
- [ ] `open`/`close` validated as time strings — raise `ValidationError` on invalid format

---

### TASK-025 — `python manage.py seed_data`
**Plan Ref:** Step 25 | **Priority:** HIGH | **Effort:** M

- [ ] Idempotent: `update_or_create` throughout
- [ ] Seeds: Countries, Cities (GPS centroids + bounding boxes), Areas, Landmarks (≥3 aliases each)
- [ ] Seeds: Tags (all 6 types), Subscription packages (SILVER/GOLD/DIAMOND/PLATINUM)
- [ ] Progress output per entity + summary
- [ ] Exit code 0 on success, 1 on error

> ⚠️ Subscription packages seeded here — NOT in a migration. Wrap each block in `try/except` with specific error logging.

---

### TASK-026 — OpenAPI via `drf-spectacular`
**Plan Ref:** Step 26 | **Priority:** HIGH | **Effort:** S

- [ ] All views: `@extend_schema(tags=[...], summary="...", responses={...})`
- [ ] Schema at `/api/v1/schema/`, Swagger UI at `/api/v1/docs/`
- [ ] Custom envelope response shape documented

---

## SESSION A-S8 — Tests + CI (Steps 27–31)

### TASK-027 — `pytest.ini` + `tests/factories.py`
**Plan Ref:** Step 27 | **Priority:** CRITICAL | **Effort:** S

- [ ] `pytest.ini`: `DJANGO_SETTINGS_MODULE=config.settings.test`, `--cov-fail-under=80`
- [ ] `factory_boy` factories for ALL models: `AdminUserFactory`, `VendorFactory`, `CityFactory`, `AreaFactory`, `LandmarkFactory`, `TagFactory`, `ImportBatchFactory`, `FieldVisitFactory`, `FieldPhotoFactory`, `AuditLogFactory`
- [ ] `VendorFactory` generates encrypted phone number via `core.encryption.encrypt`

---

### TASK-028 — Unit tests: 10 Business Rules (R1–R10)
**Plan Ref:** Step 28 | **Priority:** CRITICAL | **Effort:** M

Dedicated test class per rule:

- [ ] **R1 — `TestPostGISDistanceOnly`**: `ST_Distance(geography=True)` used, never degree × constant
- [ ] **R2 — `TestAES256GCMEncryption`**: round-trip, empty string, wrong key raises `EncryptionError`
- [ ] **R3 — `TestForRolesRBAC`**: `for_roles()` returns correct class, blocks wrong roles, permits correct
- [ ] **R4 — `TestServicesOnlyLogic`**: views return 200 without business logic (mock services)
- [ ] **R5 — `TestAuditLogImmutable`**: `AuditLog.objects.update()` raises `NotImplementedError`
- [ ] **R6 — `TestSoftDeleteOnly`**: `vendor.delete()` sets `is_deleted=True`, record still in DB
- [ ] **R7 — `TestPsycopg2Compiled`**: `production.txt` does not contain string `psycopg2-binary`
- [ ] **R8 — `TestCSVNeverOnBroker`**: import task receives `batch_id` only, reads from S3
- [ ] **R9 — `TestErrorLogCap`**: `append_error_log` stops at 1000 entries
- [ ] **R10 — `TestCeleryBeatReplicas`**: `docker-compose.yml` `celery-beat` replicas == 1

---

### TASK-029 — RBAC integration tests
**Plan Ref:** Step 29 | **Priority:** CRITICAL | **Effort:** M

- [ ] Parametrized: for each endpoint × each role → assert 403 (forbidden) or 200/201 (permitted)
- [ ] All 7 `AdminRole` values tested against all protected endpoints
- [ ] No real external APIs — all mocked
- [ ] Lockout: 5 failed login attempts → 429 with `Retry-After` header

---

### TASK-030 — Celery task tests
**Plan Ref:** Step 30 | **Priority:** HIGH | **Effort:** M

- [ ] `CELERY_TASK_ALWAYS_EAGER=True` in `test.py`
- [ ] `moto` for S3 mocking — no real AWS calls
- [ ] `freezegun` for time-dependent tasks
- [ ] Idempotency: calling import task twice on same batch → processes only once
- [ ] Error log cap: 1001 errors → only 1000 stored
- [ ] Retry: task failure triggers retry with exponential backoff

---

### TASK-031 — `.github/workflows/ci.yml`
**Plan Ref:** Step 31 | **Priority:** HIGH | **Effort:** S

- [ ] Parallel jobs: lint → migration-check → test (≥80% coverage) → security-scan → frontend-lint → frontend-build
- [ ] All jobs must pass — no partial green
- [ ] `pytest --cov-fail-under=80` enforced
- [ ] Security scan: `bandit` or `safety check`
- [ ] Migration check: `python manage.py migrate --check`

---

## Phase A Quality Gate Checklist

Before marking Phase A complete and starting Phase B:

**Backend:**
- [ ] Every model: UUID PK, `created_at`, `updated_at` where appropriate
- [ ] Every mutating view creates an AuditLog entry
- [ ] All 10 business rules (R1–R10) enforced and tested
- [ ] `RolePermission.for_roles()` on every view
- [ ] GPS: PostGIS PointField — never separate lat/lng floats
- [ ] Phone numbers: AES-256-GCM encrypted at rest
- [ ] No `TODO`, `pass`, or stub in any production path
- [ ] Health check returns 503 on DB or cache failure
- [ ] `CONN_MAX_AGE=60` in database config
- [ ] GiST spatial indexes via `migrations.RunSQL` for all PointField columns
- [ ] `psycopg2` (compiled) in `production.txt` — NOT `psycopg2-binary`
- [ ] `error_log` in ImportBatch capped at 1000 entries
- [ ] Business hours validated via `BusinessHoursSchema` on write
- [ ] Celery periodic schedules in code via `setup_periodic_tasks()`
- [ ] `task_failure` signal handler registered
- [ ] `RequestIDMiddleware` is FIRST middleware
- [ ] OpenAPI schema at `/api/v1/schema/`

**Tests:**
- [ ] All 10 business rules: dedicated test classes
- [ ] RBAC: 403 forbidden, 200/201 permitted
- [ ] `CELERY_TASK_ALWAYS_EAGER=True`
- [ ] Account lockout tested (5 attempts → 429)
- [ ] AES-256-GCM round-trip tested
- [ ] Coverage ≥ 80%
- [ ] No tests use real S3, Google Places, or external APIs
- [ ] factory_boy factories for all models

**Docker & CI:**
- [ ] `docker-compose up` brings full stack in one command
- [ ] No source volume mounts in production Compose
- [ ] Nginx reverse proxy — backend not directly port-exposed
- [ ] CI: lint → migration check → test ≥80% → security scan → build
- [ ] `celery-beat`: `replicas: 1`
- [ ] `.env.example`: zero literal placeholder values
