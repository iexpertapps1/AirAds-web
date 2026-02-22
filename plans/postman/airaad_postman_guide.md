# AirAd Postman Setup Guide
**Method: OpenAPI Import (Option 4)**

The backend ships a live OpenAPI 3.0 schema via `drf-spectacular`. Importing it into Postman gives 100% accurate request shapes derived directly from the real serializers — no manual maintenance required.

---

## Step 1 — Start the Backend

```bash
cd /Users/syedsmacbook/Developer/AirAds-web/airaad

# Start all services (postgres, redis, backend, celery, nginx)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run migrations if DB is fresh
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \
  -e DJANGO_SETTINGS_MODULE=config.settings.development \
  backend python manage.py migrate --noinput

# Seed reference data (countries, cities, areas, landmarks, tags)
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \
  -e DJANGO_SETTINGS_MODULE=config.settings.development \
  backend python manage.py seed_data
```

The backend is now reachable at `http://localhost` (via nginx) or `http://localhost:8000` (direct).

---

## Step 2 — Create Test Users for Each Role

Run this once to create one user per role for RBAC testing:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm \
  -e DJANGO_SETTINGS_MODULE=config.settings.development \
  backend python manage.py shell -c "
from apps.accounts.models import AdminUser, AdminRole

users = [
    ('admin@airaad.com',       'AirAd@SuperAdmin2024!',  AdminRole.SUPER_ADMIN),
    ('citymanager@airaad.com', 'AirAd@CityMgr2024!',     AdminRole.CITY_MANAGER),
    ('dataentry@airaad.com',   'AirAd@DataEntry2024!',   AdminRole.DATA_ENTRY),
    ('qa@airaad.com',          'AirAd@QAReview2024!',    AdminRole.QA_REVIEWER),
    ('fieldagent@airaad.com',  'AirAd@FieldAgent2024!',  AdminRole.FIELD_AGENT),
    ('analyst@airaad.com',     'AirAd@Analyst2024!',     AdminRole.ANALYST),
    ('support@airaad.com',     'AirAd@Support2024!',     AdminRole.SUPPORT),
]

for email, password, role in users:
    if not AdminUser.objects.filter(email=email).exists():
        AdminUser.objects.create_user(email=email, password=password, role=role, full_name=role.label)
        print(f'Created: {email} [{role}]')
    else:
        print(f'Already exists: {email}')
"
```

---

## Step 3 — Import the OpenAPI Schema into Postman

1. Open **Postman** → click **Import** (top-left)
2. Select **Link** tab
3. Enter: `http://localhost/api/v1/schema/`
   - Or if using direct backend port: `http://localhost:8000/api/v1/schema/`
4. Click **Continue** → **Import**
5. Postman generates a full collection with all 27 Phase A endpoints, grouped by tag

> **Alternative — download the schema file:**
> ```bash
> curl http://localhost/api/v1/schema/ -o airaad_openapi.yaml
> ```
> Then import the downloaded `.yaml` file via **Import → File**.

---

## Step 4 — Import the Environment File

1. In Postman → **Environments** (left sidebar) → **Import**
2. Select: `plans/postman/airaad_environment.json`
3. Click the environment name → set it as **Active**

The environment pre-fills `base_url`, all role credentials, and empty slots for auto-populated IDs.

---

## Step 5 — Attach the Collection-Level Pre-request Script

1. Click the imported collection name → **Edit**
2. Go to **Pre-request Script** tab
3. Paste the `collectionPreRequestScript` block from `airaad_test_scripts.js`

This auto-logs in as `SUPER_ADMIN` if `access_token` is missing, so you never get a 401 on the first run.

---

## Step 6 — Attach Test Scripts to Individual Requests

For each request below, open it → **Tests** tab → paste the corresponding block from `airaad_test_scripts.js`:

| Request | Script variable |
|---------|----------------|
| POST /auth/login/ | `loginTests` |
| POST /auth/login/ (lockout) | `loginLockoutTests` |
| POST /auth/refresh/ | `refreshTests` |
| POST /auth/logout/ | `logoutTests` |
| POST /auth/users/ | `createAdminUserTests` |
| POST /auth/users/ (non-SUPER_ADMIN) | `createAdminUserForbiddenTests` |
| POST /geo/countries/ | `createCountryTests` |
| POST /geo/cities/ | `createCityTests` |
| PATCH /geo/cities/{pk}/ (with slug) | `patchCitySlugImmutableTests` |
| POST /geo/areas/ | `createAreaTests` |
| POST /geo/landmarks/ | `createLandmarkTests` |
| POST /tags/ | `createTagTests` |
| POST /tags/ (tag_type=SYSTEM) | `createSystemTagRejectedTests` |
| POST /vendors/ | `createVendorTests` |
| POST /vendors/ (bad business_hours) | `createVendorInvalidHoursTests` |
| DELETE /vendors/{pk}/ | `softDeleteVendorTests` |
| PATCH /vendors/{pk}/qc-status/ | `updateQCStatusTests` |
| PATCH /vendors/{pk}/qc-status/ (DATA_ENTRY) | `updateQCStatusForbiddenTests` |
| POST /imports/ | `uploadCSVTests` |
| GET /imports/{pk}/ | `getImportBatchTests` |
| POST /field-ops/ | `createFieldVisitTests` |
| POST /field-ops/{visit_pk}/photos/upload/ | `uploadFieldPhotoTests` |
| GET /qa/dashboard/ | `qaDashboardTests` |
| GET /analytics/kpis/ | `analyticsKPITests` |
| GET /audit/ | `auditLogTests` |
| GET /health/ | `healthCheckTests` |

---

## Step 7 — RBAC Role-Switch Testing

To test that a specific role is **blocked** from an endpoint:

1. Set the environment variable `test_role` to the role you want to test:
   - In Postman: **Environments** → edit `test_role` value → e.g. `DATA_ENTRY`
2. On the request you want to test → **Pre-request Script** tab → paste `rbacSwitchRolePreRequest` from `airaad_test_scripts.js`
3. In the **Tests** tab, assert the expected status (403 for blocked, 200/201 for permitted)

**RBAC Quick Reference:**

| Endpoint | Permitted Roles | Blocked Roles |
|----------|----------------|---------------|
| POST /auth/users/ | SUPER_ADMIN | ALL others |
| POST /vendors/ | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY | QA_REVIEWER, FIELD_AGENT, ANALYST, SUPPORT |
| PATCH /vendors/{pk}/qc-status/ | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER | DATA_ENTRY, FIELD_AGENT, ANALYST, SUPPORT |
| GET /qa/dashboard/ | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER | FIELD_AGENT, ANALYST, DATA_ENTRY, SUPPORT |
| GET /analytics/kpis/ | SUPER_ADMIN, ANALYST | ALL others |
| GET /audit/ | SUPER_ADMIN, ANALYST | ALL others |
| POST /field-ops/{visit_pk}/photos/upload/ | SUPER_ADMIN, FIELD_AGENT | ALL others |
| GET /health/ | Everyone (AllowAny) | — |

---

## Step 8 — Run the Full Collection

1. Click the collection → **Run collection**
2. Select environment: **AirAd — Local Dev**
3. Run order (dependency chain):
   ```
   Health Check
   → Login (SUPER_ADMIN)
   → Create Country → Create City → Create Area → Create Landmark
   → Create Tag
   → Create Vendor
   → Upload CSV Import → Poll Import Batch
   → Create Field Visit → Upload Field Photo → List Field Photos
   → Update QC Status
   → QA Dashboard
   → Analytics KPIs
   → Audit Log
   → Logout
   ```
4. All IDs (`country_id`, `city_id`, `area_id`, `vendor_id`, etc.) are auto-populated by test scripts in sequence.

---

## Endpoint Reference (Phase A — 27 endpoints)

| # | Method | Path | Auth | Roles |
|---|--------|------|------|-------|
| 1 | POST | /api/v1/auth/login/ | None | All |
| 2 | POST | /api/v1/auth/refresh/ | None | All |
| 3 | POST | /api/v1/auth/logout/ | Bearer | All authenticated |
| 4 | GET | /api/v1/auth/profile/ | Bearer | All authenticated |
| 5 | POST | /api/v1/auth/users/ | Bearer | SUPER_ADMIN |
| 6 | GET | /api/v1/geo/countries/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 7 | POST | /api/v1/geo/countries/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 8 | GET | /api/v1/geo/cities/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 9 | POST | /api/v1/geo/cities/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 10 | GET | /api/v1/geo/cities/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 11 | PATCH | /api/v1/geo/cities/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 12 | GET | /api/v1/geo/areas/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 13 | POST | /api/v1/geo/areas/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 14 | GET | /api/v1/geo/landmarks/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 15 | POST | /api/v1/geo/landmarks/ | Bearer | SUPER_ADMIN, CITY_MANAGER |
| 16 | GET | /api/v1/tags/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 17 | POST | /api/v1/tags/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 18 | GET | /api/v1/tags/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 19 | PATCH | /api/v1/tags/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 20 | DELETE | /api/v1/tags/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 21 | GET | /api/v1/vendors/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, ANALYST |
| 22 | POST | /api/v1/vendors/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 23 | GET | /api/v1/vendors/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, FIELD_AGENT, ANALYST |
| 24 | PATCH | /api/v1/vendors/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, FIELD_AGENT |
| 25 | DELETE | /api/v1/vendors/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY, QA_REVIEWER, FIELD_AGENT |
| 26 | PATCH | /api/v1/vendors/{pk}/qc-status/ | Bearer | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER |
| 27 | GET | /api/v1/imports/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 28 | POST | /api/v1/imports/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 29 | GET | /api/v1/imports/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, DATA_ENTRY |
| 30 | GET | /api/v1/field-ops/ | Bearer | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER, FIELD_AGENT |
| 31 | POST | /api/v1/field-ops/ | Bearer | SUPER_ADMIN, CITY_MANAGER, FIELD_AGENT |
| 32 | GET | /api/v1/field-ops/{pk}/ | Bearer | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER, FIELD_AGENT |
| 33 | GET | /api/v1/field-ops/{visit_pk}/photos/ | Bearer | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER, FIELD_AGENT |
| 34 | POST | /api/v1/field-ops/{visit_pk}/photos/upload/ | Bearer | SUPER_ADMIN, FIELD_AGENT |
| 35 | GET | /api/v1/qa/dashboard/ | Bearer | SUPER_ADMIN, CITY_MANAGER, QA_REVIEWER |
| 36 | GET | /api/v1/analytics/kpis/ | Bearer | SUPER_ADMIN, ANALYST |
| 37 | GET | /api/v1/audit/ | Bearer | SUPER_ADMIN, ANALYST |
| 38 | GET | /api/v1/health/ | None | All (AllowAny) |
| 39 | GET | /api/v1/schema/ | None | OpenAPI YAML |
| 40 | GET | /api/v1/docs/ | None | Swagger UI |

---

## Key Request Payloads

### POST /api/v1/vendors/ — full payload
```json
{
  "business_name": "Karachi Biryani House",
  "slug": "karachi-biryani-house",
  "city_id": "{{city_id}}",
  "area_id": "{{area_id}}",
  "latitude": 24.8607,
  "longitude": 67.0011,
  "phone": "+923001234567",
  "description": "Famous biryani restaurant",
  "address_text": "Shop 5, Block 2, Clifton, Karachi",
  "data_source": "MANUAL_ENTRY",
  "business_hours": {
    "MON": {"open": "09:00", "close": "22:00", "is_closed": false},
    "TUE": {"open": "09:00", "close": "22:00", "is_closed": false},
    "WED": {"open": "09:00", "close": "22:00", "is_closed": false},
    "THU": {"open": "09:00", "close": "22:00", "is_closed": false},
    "FRI": {"open": "09:00", "close": "23:00", "is_closed": false},
    "SAT": {"open": "10:00", "close": "23:00", "is_closed": false},
    "SUN": {"open": "00:00", "close": "00:00", "is_closed": true}
  }
}
```

### PATCH /api/v1/vendors/{pk}/qc-status/
```json
{
  "qc_status": "APPROVED",
  "qc_notes": "Verified on-site. GPS accurate within 5m."
}
```

### POST /api/v1/imports/ — multipart/form-data
```
Key: file   Type: File   Value: vendors.csv
```
CSV columns: `business_name, longitude, latitude, city_slug, area_slug, phone, description, address_text`

### POST /api/v1/field-ops/
```json
{
  "vendor_id": "{{vendor_id}}",
  "latitude": 24.8607,
  "longitude": 67.0011,
  "visit_notes": "Confirmed active. Signage visible.",
  "visited_at": "2024-01-06T10:00:00Z"
}
```

---

## Standard Response Envelope

All responses (success and error) follow this shape:

```json
{
  "success": true,
  "data": { ... },
  "message": "Human-readable summary",
  "errors": {}
}
```

Paginated list responses:
```json
{
  "success": true,
  "count": 150,
  "next": "http://localhost/api/v1/vendors/?page=2",
  "previous": null,
  "data": [ ... ]
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "message": "field_name: This field is required.",
  "errors": { "field_name": ["This field is required."] }
}
```

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `airaad_environment.json` | Postman environment — import this |
| `airaad_test_scripts.js` | Copy-paste test scripts for each request |
| `airaad_postman_guide.md` | This guide |

> The full audit report and gap analysis is in `../AUDIT_AND_POSTMAN.md`.
