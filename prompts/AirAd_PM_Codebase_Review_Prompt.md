# AirAd — Product Manager Codebase Review Prompt
### For: @product-manager
### Output: Fixation Tasks for @skills/python-expert and @skills/frontend-expert
### Mode: READ CODEBASE ONLY — No tests, no status reports, no audit files

---

> **CRITICAL OPERATING INSTRUCTIONS:**
> - You are reviewing the **actual codebase files** — NOT any status reports, audit documents, or generated summaries
> - Do **NOT** run tests, do **NOT** read `AirAd_SDLC_Compliance_Audit_Report.md`, do **NOT** read any `*_status*`, `*_audit*`, or `*_report*` files
> - Read each source code file directly and compare what is **actually implemented** against what the requirements mandate
> - For every gap found: create a **Fixation Task** assigned to either `@skills/python-expert` or `@skills/frontend-expert`
> - If something is correctly implemented: mark it ✅ and move on — do not create a task for it

---

## SECTION 1 — WHAT TO READ (Codebase File Map)

Read the following directories and files in this exact order. Do not skip any:

### Backend (Python/Django)
```
backend/
├── config/
│   ├── settings/base.py
│   ├── settings/production.py
│   └── urls.py
├── celery_app.py
├── core/
│   ├── encryption.py
│   ├── geo_utils.py
│   ├── middleware.py
│   ├── pagination.py
│   ├── exceptions.py
│   ├── storage.py
│   ├── schemas.py
│   └── utils.py
├── apps/accounts/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   └── views.py
├── apps/geo/
│   ├── models.py
│   ├── services.py
│   └── views.py
├── apps/vendors/
│   ├── models.py
│   ├── services.py
│   └── views.py
├── apps/tags/
│   ├── models.py
│   ├── services.py
│   └── views.py
├── apps/imports/
│   ├── models.py
│   ├── tasks.py
│   ├── parsers.py
│   └── views.py
├── apps/field_ops/
│   ├── models.py
│   ├── services.py
│   └── views.py
├── apps/qa/
│   ├── models.py
│   ├── tasks.py
│   └── views.py
├── apps/audit/
│   ├── models.py
│   ├── middleware.py
│   └── utils.py
├── apps/analytics/
│   └── views.py
└── requirements/
    ├── base.txt
    └── production.txt
```

### Infrastructure
```
docker-compose.yml
docker-compose.dev.yml
backend/Dockerfile
frontend/Dockerfile
nginx/nginx.conf
.github/workflows/ci.yml
.env.example
```

### Frontend (React/TypeScript)
```
frontend/src/
├── styles/
│   └── dls-tokens.css
├── components/
│   ├── dls/
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── Table.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Drawer.tsx
│   │   ├── Toast.tsx
│   │   └── Sidebar.tsx
│   └── shared/
│       ├── EmptyState.tsx
│       └── SkeletonTable.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Geography.tsx
│   ├── Tags.tsx
│   ├── Vendors.tsx
│   ├── VendorDetail.tsx
│   ├── Imports.tsx
│   ├── FieldOps.tsx
│   ├── QA.tsx
│   ├── AuditLog.tsx
│   └── Users.tsx
├── stores/
├── api/
└── main.tsx
```

---

## SECTION 2 — REQUIREMENTS CHECKLIST TO VERIFY

For each item below, read the corresponding code and mark:
- ✅ **PASS** — correctly implemented
- ❌ **FAIL** — missing, wrong, or incomplete → create a Fixation Task
- ⚠️ **PARTIAL** — partially implemented → create a Fixation Task with specific gap

---

### BACKEND REQUIREMENTS (verify against codebase)

#### BR-01 · Project Setup
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-01-1 | Python 3.12, Django 5.x, DRF 3.15 in requirements | `requirements/base.txt` |
| BR-01-2 | PostGIS engine in settings: `django.contrib.gis.db.backends.postgis` | `config/settings/base.py` |
| BR-01-3 | `CONN_MAX_AGE = 60` in database settings | `config/settings/base.py` |
| BR-01-4 | `RequestIDMiddleware` listed FIRST in MIDDLEWARE (after SecurityMiddleware) | `config/settings/base.py` |
| BR-01-5 | `CELERY_BEAT_SCHEDULE` registered in code via `setup_periodic_tasks()` NOT settings | `celery_app.py` |
| BR-01-6 | `SIMPLE_JWT` config: access=15min, refresh=7d, ROTATE_REFRESH_TOKENS=True | `config/settings/base.py` |
| BR-01-7 | `EXCEPTION_HANDLER` pointing to `core.exceptions.custom_exception_handler` | `config/settings/base.py` |
| BR-01-8 | No `psycopg2-binary` anywhere in requirements (must be compiled `psycopg2`) | `requirements/production.txt` |
| BR-01-9 | `DEFAULT_PAGINATION_CLASS` set to `core.pagination.StandardResultsPagination` | `config/settings/base.py` |

#### BR-02 · Models — AdminUser
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-02-1 | UUID primary key on AdminUser | `apps/accounts/models.py` |
| BR-02-2 | Exactly 7 roles: SUPER_ADMIN, DATA_MANAGER, QC_REVIEWER, FIELD_AGENT, CONTENT_MODERATOR, ANALYTICS_VIEWER, IMPORT_OPERATOR | `apps/accounts/models.py` |
| BR-02-3 | `failed_login_count` integer field default=0 | `apps/accounts/models.py` |
| BR-02-4 | `locked_until` nullable DateTimeField | `apps/accounts/models.py` |
| BR-02-5 | `last_login_ip` field present | `apps/accounts/models.py` |

#### BR-03 · Models — Geographic
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-03-1 | City has `aliases` JSONField (array) | `apps/geo/models.py` |
| BR-03-2 | City has `centroid` PointField | `apps/geo/models.py` |
| BR-03-3 | City has `bounding_box` PolygonField (nullable) | `apps/geo/models.py` |
| BR-03-4 | Area has `parent_area` self-referential FK (nullable) | `apps/geo/models.py` |
| BR-03-5 | Landmark has `aliases` JSONField (array) | `apps/geo/models.py` |
| BR-03-6 | GiST spatial indexes added via `RunSQL` migration (NOT `models.Index`) | Migration files in `apps/geo/migrations/` |

#### BR-04 · Models — Vendor
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-04-1 | `gps_point` is PostGIS `PointField` — NOT separate lat/lng float fields | `apps/vendors/models.py` |
| BR-04-2 | `phone_number_encrypted` is `BinaryField` (not CharField) | `apps/vendors/models.py` |
| BR-04-3 | `qc_status` has exactly 4 choices: PENDING, APPROVED, REJECTED, NEEDS_REVIEW | `apps/vendors/models.py` |
| BR-04-4 | `qc_reviewed_by` is FK to AdminUser (NOT raw UUID CharField) | `apps/vendors/models.py` |
| BR-04-5 | `is_deleted` BooleanField default=False with `db_index=True` | `apps/vendors/models.py` |
| BR-04-6 | `data_source` choices: CSV_IMPORT, GOOGLE_PLACES, MANUAL_ENTRY, FIELD_AGENT | `apps/vendors/models.py` |
| BR-04-7 | GiST index on `gps_point` via `RunSQL` migration | Migration files |
| BR-04-8 | `business_hours` is JSONField | `apps/vendors/models.py` |
| BR-04-9 | `updated_at` has `auto_now=True` | `apps/vendors/models.py` |

#### BR-05 · Models — ImportBatch
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-05-1 | `file_key` is CharField storing S3 key only (no file content, no FileField) | `apps/imports/models.py` |
| BR-05-2 | `error_log` is JSONField | `apps/imports/models.py` |
| BR-05-3 | `created_by` is FK to AdminUser | `apps/imports/models.py` |

#### BR-06 · Models — FieldPhoto
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-06-1 | `s3_key` CharField (NOT FileField, NOT url, NOT path) | `apps/field_ops/models.py` |
| BR-06-2 | No public S3 URL stored — presigned URL generated on read | `apps/field_ops/models.py` + `services.py` |

#### BR-07 · Models — AuditLog
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-07-1 | `before_state` and `after_state` are JSONField | `apps/audit/models.py` |
| BR-07-2 | `request_id` CharField present | `apps/audit/models.py` |
| BR-07-3 | `actor` FK has `on_delete=SET_NULL` (NOT CASCADE) | `apps/audit/models.py` |
| BR-07-4 | `actor_label` CharField (snapshot of actor name at time of action) | `apps/audit/models.py` |
| BR-07-5 | No `update()` or `delete()` method on AuditLog model or manager | `apps/audit/models.py` |
| BR-07-6 | Compound index on `(target_type, target_id)` | `apps/audit/models.py` |

#### BR-08 · Core Utilities
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-08-1 | `encryption.py`: `encrypt()` returns bytes, `decrypt()` returns str | `core/encryption.py` |
| BR-08-2 | `encryption.py`: empty string input returns empty bytes (no exception) | `core/encryption.py` |
| BR-08-3 | `geo_utils.py`: uses `ST_Distance(...::geography)` — no degree × constant math anywhere | `core/geo_utils.py` |
| BR-08-4 | `middleware.py`: `RequestIDMiddleware` attaches UUID as `request.request_id` | `core/middleware.py` |
| BR-08-5 | `pagination.py`: `PAGE_SIZE = 25`, `max_page_size = 100` | `core/pagination.py` |
| BR-08-6 | `exceptions.py`: all exceptions return `{ success, data, message, errors }` envelope | `core/exceptions.py` |
| BR-08-7 | `schemas.py`: `BusinessHoursSchema` validates 7-day structure | `core/schemas.py` |
| BR-08-8 | `storage.py`: `generate_presigned_url()` returns URL, `upload_file_to_s3()` returns S3 key | `core/storage.py` |

#### BR-09 · RBAC
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-09-1 | `RolePermission` class has `for_roles()` classmethod | `apps/accounts/permissions.py` |
| BR-09-2 | `RolePermission` does NOT have `__call__` method | `apps/accounts/permissions.py` |
| BR-09-3 | No import or reference to `django-guardian` anywhere in codebase | All `permissions.py` files |
| BR-09-4 | Every view uses `permission_classes = [RolePermission.for_roles(...)]` | All `views.py` files |
| BR-09-5 | FIELD_AGENT views filter queryset to `agent=request.user` in `services.py` | `apps/field_ops/services.py` |

#### BR-10 · Authentication & Lockout
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-10-1 | Login view increments `failed_login_count` on wrong password | `apps/accounts/views.py` or `services.py` |
| BR-10-2 | After 5 failures: `locked_until = now() + 30min`, returns HTTP 429 | `apps/accounts/services.py` |
| BR-10-3 | Successful login resets `failed_login_count = 0` and `locked_until = None` | `apps/accounts/services.py` |
| BR-10-4 | Retry-After header included in 429 response | `apps/accounts/views.py` or `services.py` |
| BR-10-5 | Login creates AuditLog entry | `apps/accounts/services.py` |
| BR-10-6 | JWT token claims include `role`, `full_name`, `email` | `apps/accounts/serializers.py` |

#### BR-11 · Geographic APIs
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-11-1 | `GET /api/v1/geo/tree/?city={id}` endpoint exists | `apps/geo/urls.py` |
| BR-11-2 | `GET /api/v1/geo/cities/{id}/launch-readiness/` endpoint exists | `apps/geo/urls.py` + `views.py` |
| BR-11-3 | Launch readiness checks: areas created, vendors seeded (≥500), tags configured, QC approved ≥80% | `apps/geo/services.py` |
| BR-11-4 | Slug is auto-generated from name on create and immutable after | `apps/geo/serializers.py` or `models.py` |
| BR-11-5 | Alias count < 3 flagged in API response | `apps/geo/serializers.py` |

#### BR-12 · Vendor APIs
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-12-1 | Phone number decrypted on read, encrypted on write via `core/encryption.py` | `apps/vendors/serializers.py` |
| BR-12-2 | `DELETE /api/v1/vendors/{id}/` sets `is_deleted=True` — NOT a hard delete | `apps/vendors/views.py` or `services.py` |
| BR-12-3 | `is_deleted=True` vendors excluded from all list queries by default | `apps/vendors/services.py` or manager |
| BR-12-4 | `business_hours` validated via `BusinessHoursSchema` on every write | `apps/vendors/serializers.py` or `services.py` |
| BR-12-5 | QC approve/reject/flag endpoints exist with correct role gates | `apps/vendors/urls.py` + `views.py` |
| BR-12-6 | QC reject requires non-empty `qc_notes` | `apps/vendors/services.py` |
| BR-12-7 | All vendor mutations create AuditLog with before + after state | `apps/vendors/services.py` |

#### BR-13 · Import Engine
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-13-1 | Celery task receives ONLY `batch_id` — not file content or file path | `apps/imports/tasks.py` |
| BR-13-2 | Task reads CSV directly from S3 using `file_key` from ImportBatch | `apps/imports/tasks.py` |
| BR-13-3 | Task checks `ImportBatch.status != PROCESSING` before starting (idempotency guard) | `apps/imports/tasks.py` |
| BR-13-4 | Per-row error appended to `error_log` — batch continues on single-row failure | `apps/imports/tasks.py` |
| BR-13-5 | `error_log` capped at 1000 entries (no unbounded growth) | `apps/imports/tasks.py` |
| BR-13-6 | CSV columns validated: business_name, address_text, latitude, longitude, phone_number, city_slug, area_slug | `apps/imports/parsers.py` |

#### BR-14 · QA & GPS Drift
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-14-1 | `weekly_gps_drift_scan` Celery task exists scheduled for Sunday 02:00 UTC | `celery_app.py` or `apps/qa/tasks.py` |
| BR-14-2 | `daily_duplicate_scan` Celery task exists scheduled for daily 03:00 UTC | `celery_app.py` or `apps/qa/tasks.py` |
| BR-14-3 | GPS drift uses `ST_Distance(...::geography) > 20` — NOT degree × constant | `apps/qa/tasks.py` |
| BR-14-4 | Duplicate detection: ≥85% name similarity within 50m | `apps/qa/tasks.py` |
| BR-14-5 | Duplicate scan capped at 100 comparisons per vendor | `apps/qa/tasks.py` |
| BR-14-6 | `task_failure` signal handler registered in `celery_app.py` | `celery_app.py` |

#### BR-15 · Audit Trail
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-15-1 | AuditLog entries created for all POST, PATCH, DELETE operations | `apps/*/services.py` (spot check 3 apps) |
| BR-15-2 | System/Celery entries use `actor=None`, `actor_label='SYSTEM_CELERY'` | `apps/qa/tasks.py` + `apps/imports/tasks.py` |
| BR-15-3 | `log_action()` utility exists in `apps/audit/utils.py` | `apps/audit/utils.py` |
| BR-15-4 | Audit endpoint `GET /api/v1/audit/logs/` restricted to SUPER_ADMIN | `apps/audit/views.py` |

#### BR-16 · Health Check & OpenAPI
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-16-1 | `GET /api/v1/health/` is unauthenticated | `apps/` health check view |
| BR-16-2 | Health check returns HTTP 503 when DB is down | Health check view |
| BR-16-3 | OpenAPI schema at `/api/v1/schema/` | `config/urls.py` |
| BR-16-4 | Swagger UI at `/api/v1/docs/` | `config/urls.py` |

#### BR-17 · Docker & DevOps
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-17-1 | Backend Dockerfile uses multi-stage build | `backend/Dockerfile` |
| BR-17-2 | Frontend Dockerfile: production stage uses `nginx:alpine` NOT `npm run dev` | `frontend/Dockerfile` |
| BR-17-3 | Production `docker-compose.yml` has NO source volume mounts | `docker-compose.yml` |
| BR-17-4 | `celery-beat` service has `deploy.replicas: 1` | `docker-compose.yml` |
| BR-17-5 | `docker-compose.dev.yml` has source volume mounts for hot reload | `docker-compose.dev.yml` |
| BR-17-6 | `.env.example` has zero literal placeholder values | `.env.example` |
| BR-17-7 | `.dockerignore` exists for both backend and frontend | root directory |

#### BR-18 · CI/CD
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| BR-18-1 | CI pipeline has: lint, migration-check, test, security-scan, build jobs | `.github/workflows/ci.yml` |
| BR-18-2 | `pytest --cov-fail-under=80` enforced in CI | `.github/workflows/ci.yml` |
| BR-18-3 | `bandit` and `safety` included in security-scan job | `.github/workflows/ci.yml` |
| BR-18-4 | Test job uses postgres:16-postgis and redis:7 services | `.github/workflows/ci.yml` |

---

### FRONTEND REQUIREMENTS (verify against codebase)

#### FR-01 · DLS Token File
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-01-1 | `dls-tokens.css` exists in `src/styles/` | `frontend/src/styles/dls-tokens.css` |
| FR-01-2 | `--color-rausch: #FF5A5F` defined as CSS custom property | `dls-tokens.css` |
| FR-01-3 | `--color-babu: #00A699` defined | `dls-tokens.css` |
| FR-01-4 | `--color-arches: #FC642D` defined | `dls-tokens.css` |
| FR-01-5 | `--color-grey-50: #F7F7F7` defined (page background) | `dls-tokens.css` |
| FR-01-6 | `--color-hof: #484848` defined (primary text) | `dls-tokens.css` |
| FR-01-7 | `dls-tokens.css` imported FIRST in `main.tsx` before any component | `frontend/src/main.tsx` |
| FR-01-8 | No hardcoded hex values in ANY component file | Spot check 5 component files |

#### FR-02 · DLS Components
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-02-1 | `Button.tsx`: has Primary, Secondary, Destructive, Ghost variants | `components/dls/Button.tsx` |
| FR-02-2 | `Button.tsx`: loading state with spinner | `components/dls/Button.tsx` |
| FR-02-3 | `Badge.tsx`: success/warning/error/info/neutral variants each with icon | `components/dls/Badge.tsx` |
| FR-02-4 | `Table.tsx`: has EmptyState slot and SkeletonRows (no spinner for initial load) | `components/dls/Table.tsx` |
| FR-02-5 | `Table.tsx`: sortable column headers | `components/dls/Table.tsx` |
| FR-02-6 | `Modal.tsx`: focus trap implemented (TAB key stays inside modal) | `components/dls/Modal.tsx` |
| FR-02-7 | `Modal.tsx`: closes on ESC key | `components/dls/Modal.tsx` |
| FR-02-8 | `Drawer.tsx`: 640px width from right side | `components/dls/Drawer.tsx` |
| FR-02-9 | `Sidebar.tsx`: nav item border-radius `0 100px 100px 0` (pill-right) | `components/dls/Sidebar.tsx` |
| FR-02-10 | `Toast.tsx`: auto-dismisses after 4 seconds | `components/dls/Toast.tsx` |
| FR-02-11 | Icons use `lucide-react` ONLY — no other icon libraries | Spot check all component imports |
| FR-02-12 | Icon stroke-width is 1.5 throughout | Spot check component files |

#### FR-03 · Accessibility
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-03-1 | All icon-only buttons have `aria-label` | Spot check Button usage in pages |
| FR-03-2 | All table columns have `aria-sort` on sortable headers | `components/dls/Table.tsx` |
| FR-03-3 | Skip-to-main-content link as first focusable element | `main.tsx` or layout component |
| FR-03-4 | `prefers-reduced-motion` media query disables all CSS animations | `dls-tokens.css` or global CSS |

#### FR-04 · Axios & API Layer
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-04-1 | Axios interceptor attaches `Authorization: Bearer {token}` to all requests | `src/api/` |
| FR-04-2 | Axios interceptor on 401: attempts refresh, then redirects to /login on failure | `src/api/` |
| FR-04-3 | TanStack Query used for data fetching — NOT raw useEffect + fetch | Spot check 3 pages |

#### FR-05 · Page — Platform Health Dashboard (`/`)
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-05-1 | Hero metric: Total Verified Vendors with % change vs last week | `pages/Dashboard.tsx` |
| FR-05-2 | 4 metric cards: Pending QC, Import Success Rate, Drift Flags, Field Visits | `pages/Dashboard.tsx` |
| FR-05-3 | Donut chart using Recharts for QC status breakdown | `pages/Dashboard.tsx` |
| FR-05-4 | Choropleth map using Leaflet + react-leaflet for vendors per city | `pages/Dashboard.tsx` |
| FR-05-5 | Import activity line chart (Recharts) with 7d/14d/30d toggle | `pages/Dashboard.tsx` |
| FR-05-6 | Recent Activity Feed showing last 10 AuditLog entries | `pages/Dashboard.tsx` |
| FR-05-7 | Skeleton loading on all data areas (no spinners) | `pages/Dashboard.tsx` |
| FR-05-8 | Auto-refresh every 60 seconds (React Query `refetchInterval`) | `pages/Dashboard.tsx` |

#### FR-06 · Page — Geographic Management
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-06-1 | Collapsible tree: Country → City → Area → Landmark in left panel | `pages/Geography.tsx` |
| FR-06-2 | City detail: Leaflet map with centroid + bounding box | `pages/Geography.tsx` |
| FR-06-3 | Warning badge if aliases count < 3 | `pages/Geography.tsx` |
| FR-06-4 | Launch Readiness checklist display | `pages/Geography.tsx` |
| FR-06-5 | "Launch City" button disabled until all readiness criteria pass | `pages/Geography.tsx` |

#### FR-07 · Page — Tag Management
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-07-1 | Tag Type displayed as colored badge per type | `pages/Tags.tsx` |
| FR-07-2 | SYSTEM tags in separate read-only section (no create/edit/delete controls) | `pages/Tags.tsx` |
| FR-07-3 | Tag usage sparkline chart in usage detail modal | `pages/Tags.tsx` |
| FR-07-4 | Bulk activate/deactivate as background job with progress toast | `pages/Tags.tsx` |

#### FR-08 · Page — Vendor Oversight
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-08-1 | Vendor detail is a FULL PAGE (not a modal) with 6 tabs | `pages/VendorDetail.tsx` |
| FR-08-2 | Tab 6 — Internal Notes: only visible to SUPER_ADMIN + QC_REVIEWER | `pages/VendorDetail.tsx` |
| FR-08-3 | QC Queue (Sidebar item): shows only PENDING + NEEDS_REVIEW, sorted oldest first | `pages/Vendors.tsx` or separate page |
| FR-08-4 | QC Queue sidebar item shows count badge | `components/dls/Sidebar.tsx` or `pages/Vendors.tsx` |
| FR-08-5 | Phone number masked in vendor list (not plain text) | `pages/Vendors.tsx` |

#### FR-09 · Page — Import Management
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-09-1 | Drag-and-drop CSV upload | `pages/Imports.tsx` |
| FR-09-2 | PapaParse client-side CSV validation before upload | `pages/Imports.tsx` |
| FR-09-3 | Auto-refresh every 10s for QUEUED/PROCESSING jobs | `pages/Imports.tsx` |
| FR-09-4 | Progress bar showing `processed_rows / total_rows` | `pages/Imports.tsx` |

#### FR-10 · Page — QA Dashboard
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-10-1 | "Run GPS Drift Scan Now" button visible only to SUPER_ADMIN | `pages/QA.tsx` |
| FR-10-2 | Duplicate flags: side-by-side comparison modal | `pages/QA.tsx` |
| FR-10-3 | Merge wizard available for DATA_MANAGER + SUPER_ADMIN only | `pages/QA.tsx` |

#### FR-11 · Page — Audit Log
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-11-1 | Page is only accessible/visible to SUPER_ADMIN | `pages/AuditLog.tsx` + routing |
| FR-11-2 | Row expansion shows before/after JSON diff (react-diff-viewer or similar) | `pages/AuditLog.tsx` |
| FR-11-3 | No edit or delete buttons anywhere on this page | `pages/AuditLog.tsx` |
| FR-11-4 | Export CSV button present (max 10,000 records) | `pages/AuditLog.tsx` |

#### FR-12 · Page — User Management
| # | Requirement | Where to verify |
|---|-------------|-----------------|
| FR-12-1 | Page only accessible to SUPER_ADMIN | `pages/Users.tsx` + routing |
| FR-12-2 | Create user: auto-generated password shown once only | `pages/Users.tsx` |
| FR-12-3 | Unlock Account action available with confirmation modal | `pages/Users.tsx` |

---

## SECTION 3 — HOW TO FORMAT YOUR FINDINGS

After reading all codebase files above and checking every requirement, produce your output in this exact format:

---

### REVIEW SUMMARY

```
Total Requirements Checked: ___
✅ PASS: ___
❌ FAIL: ___
⚠️ PARTIAL: ___
```

---

### FIXATION TASKS FOR @skills/python-expert

> One task card per backend gap. Be specific about the file, the exact problem, and the exact fix needed.

---

#### TASK PY-001 · [Short Title]

**File:** `apps/accounts/models.py` *(example)*
**Requirement:** BR-02-3 — `failed_login_count` must be IntegerField with default=0
**Current State:** Field is missing / wrong type / default not set *(describe what you actually found)*
**Required Fix:**
```python
# Exact change needed — be precise
failed_login_count = models.IntegerField(default=0)
```
**Priority:** CRITICAL / HIGH / MEDIUM *(based on impact on business rules)*
**Blocks:** *(list any other requirements or tasks that depend on this fix)*

---

#### TASK PY-002 · [Short Title]
*(continue for each backend gap found)*

---

### FIXATION TASKS FOR @skills/frontend-expert

> One task card per frontend gap. Be specific about the file, the exact problem, and the exact fix needed.

---

#### TASK FE-001 · [Short Title]

**File:** `frontend/src/components/dls/Modal.tsx` *(example)*
**Requirement:** FR-02-6 — Focus trap must be implemented (TAB key stays inside modal)
**Current State:** Focus trap logic missing / using wrong library / ESC key not wired *(describe what you actually found)*
**Required Fix:**
```tsx
// Exact change needed — be precise
// e.g., import { useFocusTrap } from 'focus-trap-react'
// wrap modal content with <FocusTrap>
```
**Priority:** CRITICAL / HIGH / MEDIUM
**Blocks:** *(list dependencies)*

---

#### TASK FE-002 · [Short Title]
*(continue for each frontend gap found)*

---

## SECTION 4 — PRIORITY CLASSIFICATION GUIDE

Use this guide when assigning priority to each Fixation Task:

| Priority | Criteria |
|----------|----------|
| **CRITICAL** | Blocks data integrity (GPS stored wrong), security (phone not encrypted, lockout missing), or the system cannot function (wrong DB engine, broken RBAC) |
| **HIGH** | Business rule violated (soft delete not working, audit log not created, wrong pagination), or core workflow broken (CSV import crashes, QC flow broken) |
| **MEDIUM** | UI gap that affects operator efficiency (missing empty state, wrong badge color, no skeleton loader, missing filter), or API response format mismatch |
| **LOW** | DLS cosmetic issues (wrong font size, wrong spacing, icon stroke width), non-critical configuration issues |

---

## SECTION 5 — FINAL INSTRUCTIONS FOR @product-manager

1. **Read every file listed in Section 1** — open and scan the actual source code
2. **Do NOT run any test commands** — static code review only
3. **Do NOT read** `AirAd_SDLC_Compliance_Audit_Report.md`, `AirAd_*_status*`, or any `*_report*` files — they may be outdated
4. **Check each row** in the Section 2 tables — mark ✅, ❌, or ⚠️
5. **For every ❌ and ⚠️**: create a Fixation Task in Section 3 format
6. **Group tasks correctly**: Django/Python gaps → `@skills/python-expert`, React/TypeScript/CSS gaps → `@skills/frontend-expert`
7. **Infrastructure gaps** (Dockerfile, docker-compose, CI): assign to `@skills/python-expert`
8. **Be specific in every task card** — include exact file path, exact requirement ID, exact current state, exact fix needed
9. **Do not duplicate**: if one fix resolves two requirements, note both requirement IDs in one task card
10. **Deliver the final output** as: REVIEW SUMMARY → FIXATION TASKS FOR @skills/python-expert → FIXATION TASKS FOR @skills/frontend-expert

---

*AirAd PM Codebase Review Prompt — v1.0*
*Authority: AirAd_Master_Super_Prompt_MERGED.md (Unified Edition v3.0)*
*Source of Truth: AirAd Specification Documents DOC-1 through DOC-4*
*Mode: Static code review only — no test execution, no audit file reading*
