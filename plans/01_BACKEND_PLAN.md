# AirAd — Backend Build Plan
## Enterprise-Grade, Production-Ready Django Backend
### Phase A (Data Collection Portal) → Phase B (Full Public Platform)

---

## 0. ANALYSIS SUMMARY

**Phase A** — Internal admin portal: 7-role RBAC, vendor data collection, CSV import engine, GPS QA, field operations, audit trail.

**Phase B** — Public platform: Customer/Vendor OTP auth, discovery search engine (geospatial ranking), discount automation, voice bot, subscriptions, analytics.

**Non-negotiable rules (from audit):**
- PostGIS `ST_Distance` ONLY — never degree × constant
- AES-256-GCM for all phone numbers at rest
- `for_roles()` class factory — the only RBAC mechanism
- All business logic in `services.py` — never in views or serializers
- AuditLog on every POST/PATCH/DELETE — immutable, forever
- Soft deletes only — `is_deleted=True`, never hard delete
- `psycopg2` (compiled) in production — never `psycopg2-binary`
- CSV content never passed over Celery broker — pass `batch_id` only
- `error_log` in ImportBatch capped at 1000 entries
- `celery-beat` replicas: 1 always

---

## 1. PROJECT STRUCTURE

```
airaad/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py          # Shared settings
│   │   │   ├── production.py    # PostgreSQL, S3, no DEBUG
│   │   │   ├── development.py   # Dev override
│   │   │   └── test.py          # CELERY_TASK_ALWAYS_EAGER=True
│   │   ├── urls.py
│   │   └── asgi.py
│   ├── celery_app.py            # Celery + task_failure signal + Beat schedules
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
│       ├── encryption.py        # AES-256-GCM
│       ├── geo_utils.py         # PostGIS ST_Distance wrappers
│       ├── middleware.py        # RequestIDMiddleware (FIRST)
│       ├── pagination.py        # StandardResultsPagination (25)
│       ├── exceptions.py        # custom_exception_handler
│       ├── storage.py           # S3 presigned URL helpers
│       ├── schemas.py           # Pydantic BusinessHoursSchema
│       └── utils.py             # get_client_ip, vendor_has_feature
├── frontend/
├── mobile/
├── nginx/nginx.conf
├── docker-compose.yml           # Production
├── docker-compose.dev.yml       # Dev override
├── .env.example                 # Zero literal placeholders
└── README.md
```

---

## 2. PHASE A — BUILD SEQUENCE (39 Steps)

### Steps 1–4: Infrastructure

**Step 1 — `.env.example` + README**
- Zero literal placeholder values — only generation instructions
- Documents: SECRET_KEY generation, ENCRYPTION_KEY generation (32-byte base64), DB, Redis, AWS

**Step 2 — Docker Compose**
- `docker-compose.yml` (production):
  - Services: postgres (PostGIS image), redis, backend, celery-worker, celery-beat, frontend (nginx), nginx
  - `celery-beat`: `deploy.replicas: 1` — exactly one, always
  - No source code volume mounts in production
  - Health checks: `pg_isready` for postgres, `redis-cli ping` for redis
  - Backend not directly port-exposed (nginx reverse proxy)
- `docker-compose.dev.yml` (override): source code mounts, `runserver`, `npm run dev`

**Step 3 — Dockerfiles**
- Backend (multi-stage):
  - Stage 1 (builder): `python:3.12-slim`, compile `psycopg2` (NOT binary)
  - Stage 2 (production): `python:3.12-slim` + GDAL (version must match PostGIS image exactly)
  - CMD: `gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4`
- Frontend (multi-stage): `node:20-alpine` build → `nginx:alpine` serve (never `npm run dev`)

**Step 4 — Nginx config**
- `/api/` → backend:8000, `/` → frontend:80

---

### Steps 5–9: Requirements, Settings, Celery, Core

**Step 5 — `requirements/` files**
```
base.txt       → Django 5.x, DRF 3.15, SimpleJWT, drf-spectacular, django-environ,
                  Pydantic, Celery 5.x, redis, django-storages, boto3
production.txt → base + psycopg2 (compiled), gunicorn
development.txt→ base + psycopg2-binary, django-extensions, ipython
test.txt       → development + pytest-django, factory_boy, moto, freezegun, coverage
```

**Step 6 — `config/settings/`**
- `base.py`:
  - `ENGINE: django.contrib.gis.db.backends.postgis` (GeoDjango — mandatory)
  - `CONN_MAX_AGE: 60`
  - `SIMPLE_JWT`: ACCESS=15min, REFRESH=7days, `ROTATE_REFRESH_TOKENS=True`
  - `EXCEPTION_HANDLER: core.exceptions.custom_exception_handler`
  - `RequestIDMiddleware` FIRST in MIDDLEWARE
  - `DEFAULT_PAGINATION_CLASS: core.pagination.StandardResultsPagination`
- `production.py`: PostgreSQL, S3 storage, DEBUG=False
- `development.py`: local DB, DEBUG=True
- `test.py`: test DB, `CELERY_TASK_ALWAYS_EAGER=True`, dummy AWS vars

**Step 7 — `config/urls.py`**
All URL prefixes: `/api/v1/auth/`, `/api/v1/geo/`, `/api/v1/tags/`, `/api/v1/vendors/`, `/api/v1/imports/`, `/api/v1/field-ops/`, `/api/v1/qa/`, `/api/v1/analytics/`, `/api/v1/audit/`, `/api/v1/health/`, `/api/v1/schema/`, `/api/v1/docs/`

**Step 8 — `celery_app.py`**
- App instance with `autodiscover_tasks`
- `setup_periodic_tasks()` registers Beat schedules in code:
  - `weekly_gps_drift_scan`: Sunday 02:00 UTC
  - `daily_duplicate_scan`: daily 03:00 UTC
  - `discount_scheduler`: every 1 minute (Phase B)
  - `subscription_expiry_check`: daily midnight UTC (Phase B)
  - `hourly_tag_assignment`: every 1 hour (Phase B)
- `task_failure` signal handler: structured log with task name, args, exception

**Step 9 — `core/` utilities**

| Module | Purpose |
|---|---|
| `encryption.py` | `encrypt(str)->bytes`, `decrypt(bytes)->str`. AES-256-GCM. Randomised IV. Empty string → empty bytes. |
| `geo_utils.py` | `calculate_drift_distance(a,b)->float` via `ST_Distance(::geography)`. `find_nearby_vendors(center, radius)->QuerySet` via `ST_DWithin`. NEVER degree×constant. |
| `middleware.py` | `RequestIDMiddleware`: UUID per request, `X-Request-ID` header, stored on `request.request_id`. MUST be FIRST. |
| `pagination.py` | `StandardResultsPagination`: PAGE_SIZE=25, max=100 |
| `exceptions.py` | `custom_exception_handler`: all DRF exceptions → `{success, data, message, errors}` |
| `schemas.py` | `BusinessHoursSchema` (Pydantic): validates 7-day hours JSON on every write |
| `storage.py` | `generate_presigned_url(key, expiry=3600)`, `upload_file_to_s3(file, prefix)->key` |
| `utils.py` | `get_client_ip(request)`, `vendor_has_feature(vendor, feature)->bool` (Phase B) |

---

### Steps 10–17: Database Models

**Step 10 — `apps/accounts/models.py`**
```
AdminUser (AbstractBaseUser):
  id(UUID PK), email(unique), full_name, role(7 choices),
  is_active, failed_login_count(int default 0),
  locked_until(datetime nullable), last_login_ip, created_at, updated_at
```

**Step 11 — `apps/accounts/permissions.py`**
```python
class RolePermission(BasePermission):
    allowed_roles: tuple[AdminRole, ...]

    @classmethod
    def for_roles(cls, *roles):
        return type('DynamicRolePermission', (cls,), {'allowed_roles': roles})

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role in self.allowed_roles)
```

**Step 12 — Auth views + serializers + URLs**
- Login with lockout logic (5 failures → 429 + `Retry-After`)
- JWT: custom serializer adds `role`, `full_name`, `email` to claims
- All auth events → AuditLog

**Step 13 — `apps/audit/models.py` + middleware + utils**
```
AuditLog: id(UUID), action(indexed), actor(FK nullable SET_NULL),
  actor_label(snapshot), target_type, target_id(UUID nullable),
  before_state(JSON), after_state(JSON), request_id, ip_address,
  created_at(indexed). IMMUTABLE.
Indexes: (target_type, target_id), (actor, created_at)
```
- `log_action(action, actor, target_obj, request, before, after)` utility
- Called explicitly from `services.py`

**Step 14 — `apps/geo/models.py` + migrations**
```
Country: id(UUID), name, code(ISO-2), is_active, created_at
City: id(UUID), country(FK), name, slug(immutable after create),
      aliases(JSONField[]), centroid(PointField), bounding_box(PolygonField nullable),
      is_active, display_order, created_at
Area: id(UUID), city(FK), parent_area(FK self nullable), name, slug,
      aliases(JSONField[]), centroid(PointField nullable), is_active, created_at
Landmark: id(UUID), area(FK), name, slug, aliases(JSONField[]),
          location(PointField), is_active, created_at
ALL PointField → GiST spatial index via migrations.RunSQL (NOT models.Index)
```

**Step 15 — `apps/tags/models.py`**
```
Tag: id(UUID), name, slug(immutable), tag_type(LOCATION/CATEGORY/INTENT/PROMOTION/TIME/SYSTEM),
     display_label, display_order, icon_name, is_active, created_at
SYSTEM tags: cannot be created/edited/deleted via API
```

**Step 16 — `apps/vendors/models.py`**
```
Vendor: id(UUID), business_name, slug, description,
  gps_point(PointField, GiST via RunSQL), address_text,
  city(FK), area(FK), landmark(FK nullable),
  phone_number_encrypted(BinaryField — AES-256-GCM),
  business_hours(JSONField — validated via BusinessHoursSchema),
  qc_status(PENDING/APPROVED/REJECTED/NEEDS_REVIEW),
  qc_reviewed_by(FK AdminUser nullable — NOT raw UUID), qc_reviewed_at, qc_notes,
  data_source(CSV_IMPORT/GOOGLE_PLACES/MANUAL_ENTRY/FIELD_AGENT),
  is_deleted(boolean default False, db_index=True),
  created_at(auto_now_add), updated_at(auto_now)
Indexes: (qc_status, is_deleted), (area, is_deleted), (data_source)
```

**Step 17 — `apps/imports/models.py` + `apps/field_ops/models.py`**
```
ImportBatch: id(UUID), file_key(S3 key ONLY), status(QUEUED/PROCESSING/DONE/FAILED),
  total_rows, processed_rows, error_count, error_log(JSONField, capped 1000),
  created_by(FK AdminUser), created_at, updated_at

FieldVisit: id(UUID), vendor(FK), agent(FK AdminUser), visited_at,
  visit_notes, gps_confirmed_point(PointField nullable), created_at

FieldPhoto: id(UUID), field_visit(FK), s3_key(CharField),
  caption, is_active(default True), uploaded_at
  (presigned URL generated on read — never stored as public URL)
```

---

### Steps 18–23: Services, Serializers, Views, Tasks

**Step 18 — All `services.py` files**
- All domain logic lives here — views only call services
- Each app has its own `services.py`
- Every mutation calls `log_action()` from `apps/audit/utils.py`

**Step 19 — All DRF serializers**
- Consistent JSON envelope via `custom_exception_handler`
- Phone: decrypt on read, encrypt on write in `VendorSerializer`
- GPS: accept lat/lng input, store as PointField

**Step 20 — All DRF views + ViewSets + URLs**
- Every view: `permission_classes = [RolePermission.for_roles(...)]`
- No business logic in views — all delegated to `services.py`
- All views decorated with `@extend_schema` for OpenAPI

**Step 21 — Import parsers + Celery tasks**
- `apps/imports/tasks.py`:
  - Idempotency: check `status != PROCESSING` before starting
  - Read CSV from S3 streaming — NEVER from broker payload
  - Per-row: validate → on error append to `error_log` (cap 1000) → continue
  - On success: create Vendor with `data_source=CSV_IMPORT`
  - Retry: max 3, exponential backoff

**Step 22 — QA tasks**
- `weekly_gps_drift_scan`: `ST_Distance(::geography) > 20` → `NEEDS_REVIEW` + AuditLog per vendor
- `daily_duplicate_scan`: `ST_DWithin` 50m + `difflib.SequenceMatcher ≥ 0.85` → flag. Cap: 100 comparisons/vendor

**Step 23 — Health check view**
- `GET /api/v1/health/` — unauthenticated
- DB connectivity + Redis ping
- 200 healthy / 503 degraded

---

### Steps 24–26: Schemas, Seed Data, OpenAPI

**Step 24** — `core/schemas.py`: `BusinessHoursSchema` (Pydantic)

**Step 25** — `python manage.py seed_data` (idempotent `update_or_create`):
- Countries, Cities (GPS centroids + bounding boxes), Areas, Landmarks (≥3 aliases each)
- Tags (all types), Subscription packages (SILVER/GOLD/DIAMOND/PLATINUM)
- Progress output + summary. Exit 0 on success, 1 on error.

**Step 26** — OpenAPI: `drf-spectacular`, all views with `@extend_schema`

---

### Steps 27–31: Tests + CI

**Step 27** — `pytest.ini` + `tests/factories.py` (factory_boy for all models)

**Step 28** — Unit tests R1–R10 (all 10 business rules, dedicated test classes)

**Step 29** — RBAC integration tests (parametrized, no real external APIs)

**Step 30** — Celery task tests (`CELERY_TASK_ALWAYS_EAGER=True`, moto for S3)

**Step 31** — `.github/workflows/ci.yml`:
- Parallel: lint → migration-check → test (≥80% coverage) → security-scan → frontend-lint → frontend-build
- All must pass

---

## 3. PHASE B — FULL PLATFORM EXTENSIONS

> Phase B extends Phase A — NOT a new project. New apps added, existing models extended via new migrations.

### 3.1 Additional Models

**Discount** (extend `apps/vendors/`):
- `vendor(FK)`, `title`, `discount_type`, `value`, `applies_to`, `item_description`
- `start_time`, `end_time`, `is_recurring`, `recurrence_days(JSONField[])`
- `is_active` (computed property), `min_order_value`, `created_at`

**AnalyticsEvent** (extend `apps/analytics/`):
- `event_type`, `vendor(FK nullable)`, `user(FK nullable)`, `session_id`
- `latitude`, `longitude`, `device_type`, `search_query`, `timestamp`
- **CRITICAL**: Partition by month (high-volume table)

**VoiceBotConfig** (one-to-one with Vendor):
- `menu_items(JSONField[])`, `opening_hours_summary`, `delivery_info`
- `discount_summary` (auto-updated), `custom_qa_pairs(JSONField[])`

**SubscriptionPackage**:
- `level`, `price_monthly`, `max_videos`, `daily_happy_hours_allowed`
- `has_voice_bot`, `has_sponsored_windows`, `has_predictive_reports`
- `visibility_boost_weight` (used in ranking formula)
- Seeded via management command — not migration

**Vendor Model Extensions** (new migration):
- `owner(FK Customer nullable)`, `is_claimed`, `claimed_at`
- `logo`, `cover_photo` (ImageField → S3)
- `offers_delivery`, `offers_pickup`, `is_verified`
- `subscription_level`, `subscription_valid_until`
- `total_views`, `total_profile_taps` (counters)
- `location_pending_review`

### 3.2 Customer & Vendor Auth

```
POST /api/v1/auth/customer/send-otp/    → SMS via Twilio (abstracted service class)
POST /api/v1/auth/customer/verify-otp/ → create/login, return JWT
POST /api/v1/auth/customer/profile/    → update name, email, device_token
POST /api/v1/auth/vendor/send-otp/
POST /api/v1/auth/vendor/verify-otp/
POST /api/v1/auth/vendor/verify-email/
GET  /api/v1/auth/vendor/me/
```
JWT payload includes: `user_type (CUSTOMER/VENDOR/ADMIN)`, `role`

### 3.3 Discovery & Search Engine

**`RankingService` class (pure function, independently testable):**
1. `ST_DWithin` filter FIRST
2. Score: Text match (30%) + Distance (25%) + Active offer (15%) + Popularity last 30d (15%) + Subscription (15%)
3. Subscription scores: SILVER=0.0, GOLD=0.3, DIAMOND=0.6, PLATINUM=1.0
4. Paid tier cannot override distance by more than 30%

**Endpoints:**
```
GET  /api/v1/discovery/search/?lat&lng&radius&q&tags
GET  /api/v1/discovery/nearby/?lat&lng&radius
GET  /api/v1/tags/discovery/?tag_types=...
POST /api/v1/discovery/voice-search/         → rule-based NLP, no ML
POST /api/v1/vendors/{slug}/voice-query/     → rule-based VoiceBotConfig matching
```

### 3.4 Discount & Promotion Engine

**Celery tasks:**
- `discount_scheduler` (every 1 min): auto-activate/deactivate based on `start_time`/`end_time`
- `subscription_expiry_check` (midnight UTC): downgrade expired → SILVER, send reminders at 7d + 1d

**TagAutoAssigner service:**
1. Discount activates → auto-assign PROMOTION tag
2. Discount deactivates → remove PROMOTION tag
3. Hourly cron → assign/remove TIME tags globally
4. Vendor reaches 10 views/week → assign `SYSTEM:NewVendorBoost`
5. Top 10% taps in area → assign `SYSTEM:HighEngagement`

### 3.5 Subscription Feature Gating

**`vendor_has_feature(vendor, feature_name) -> bool`** — the ONLY gate mechanism:
- Feature names: `HAPPY_HOUR`, `VOICE_BOT`, `SPONSORED_WINDOW`, `TIME_HEATMAP`, `PREDICTIVE_RECOMMENDATIONS`, `EXTRA_REELS`
- All premium API endpoints use this function — no scattered if-else

**Tier limits:**
- Silver: 1 video, no happy hours, no voice bot
- Gold: 3 videos, 1 happy hour/day, basic voice bot
- Diamond: 6 videos, 3 happy hours/day, dynamic voice bot
- Platinum: unlimited videos, unlimited happy hours, advanced voice bot

### 3.6 Analytics APIs (Phase B)

**Vendor analytics (IsVendorOwner):**
```
GET /api/v1/vendors/{id}/analytics/summary/
GET /api/v1/vendors/{id}/analytics/reels/
GET /api/v1/vendors/{id}/analytics/discounts/
GET /api/v1/vendors/{id}/analytics/time-heatmap/   → Diamond+ only
GET /api/v1/vendors/{id}/analytics/recommendations/ → Platinum only (rule-based)
```

**Admin platform analytics:**
```
GET /api/v1/admin/analytics/platform-overview/
GET /api/v1/admin/analytics/area-heatmap/{city_id}/
GET /api/v1/admin/analytics/search-terms/
```

**Rule:** NEVER block API request to record analytics. Always dispatch Celery task → return response immediately.

### 3.7 Admin Management APIs (Phase B)

```
POST /api/v1/admin/vendors/{id}/verify/
PATCH /api/v1/admin/vendors/{id}/suspend/
POST /api/v1/admin/vendors/{id}/approve-claim/
POST /api/v1/admin/vendors/{id}/reject-claim/
POST /api/v1/admin/vendors/{id}/approve-location/
POST /api/v1/admin/vendors/{id}/reject-location/
POST /api/v1/admin/geo/cities/{id}/launch/
POST /api/v1/admin/tags/bulk-assign/
```

---

## 4. QUALITY GATE CHECKLIST

Before marking any step complete, verify:

**Backend:**
- [ ] Every model: UUID PK, `created_at`, `updated_at` where appropriate
- [ ] Every mutating view creates an AuditLog entry
- [ ] All 10 business rules (R1–R10) enforced and tested
- [ ] `RolePermission.for_roles()` on every view — no `__call__` method
- [ ] GPS: PostGIS PointField — never separate lat/lng floats
- [ ] Phone numbers: AES-256-GCM encrypted at rest
- [ ] No TODO, pass, or stub in any production path
- [ ] Health check returns 503 on DB or cache failure
- [ ] `CONN_MAX_AGE=60` in database config
- [ ] GiST spatial indexes via `migrations.RunSQL` for all PointField columns
- [ ] `psycopg2` (compiled) in `requirements/production.txt` — NOT `psycopg2-binary`
- [ ] `error_log` in ImportBatch capped at 1000 entries
- [ ] Business hours validated via `BusinessHoursSchema` on write
- [ ] Celery periodic schedules in code via `setup_periodic_tasks()`
- [ ] `task_failure` signal handler registered in `celery_app.py`
- [ ] `RequestIDMiddleware` is FIRST middleware
- [ ] All 7 AdminRole values match RBAC matrix exactly
- [ ] OpenAPI schema accessible at `/api/v1/schema/`

**Tests:**
- [ ] All 10 business rules: dedicated test classes
- [ ] RBAC: forbidden 403, permitted 200/201
- [ ] Celery tasks: `CELERY_TASK_ALWAYS_EAGER=True`
- [ ] Account lockout tested (5 attempts → 429)
- [ ] AES-256-GCM round-trip tested
- [ ] Coverage ≥ 80% enforced by `--cov-fail-under=80`
- [ ] No tests use real S3, Google Places, or external APIs
- [ ] factory_boy factories for all models

**Docker & CI:**
- [ ] `docker-compose up` brings full stack in one command
- [ ] No source volume mounts in production Compose
- [ ] Nginx reverse proxy — backend not directly port-exposed
- [ ] CI: lint → migration check → test ≥80% → security scan → build
- [ ] `celery-beat`: `replicas: 1` in Compose deploy config
- [ ] `.env.example`: zero literal placeholder values

---

## 5. SESSION BUILD ORDER

| Session | Steps | Goal |
|---|---|---|
| A-S1 | 1–4 | Docker + Nginx + env |
| A-S2 | 5–9 | Requirements + Settings + Celery + Core |
| A-S3 | 10–13 | Accounts + Permissions + Auth + Audit |
| A-S4 | 14–17 | Geo + Tags + Vendors + Imports models |
| A-S5 | 18–20 | All services.py + Serializers + Views |
| A-S6 | 21–23 | Import/QA tasks + Health check |
| A-S7 | 24–26 | Schemas + Seed + OpenAPI |
| A-S8 | 27–31 | All tests + CI pipeline |
| **GATE** | — | `docker-compose up` → `pytest --cov-fail-under=80` → all green |
| B-S1 | — | New models + Customer/Vendor auth |
| B-S2 | — | Vendor APIs + Discovery/Search engine |
| B-S3 | — | Discount engine + Tag auto-assignment |
| B-S4 | — | Admin APIs + Analytics + Subscriptions |
