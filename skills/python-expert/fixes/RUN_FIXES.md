# AirAd Backend — Audit Fixes: Execution Prompt
## For: `skills/python-expert` Agent | Session: A-S8
## Read this file first. Execute each task in the order listed below.

---

## CONTEXT

The AirAd backend (Phase A) is functionally complete (TASK-001 through TASK-026). A post-build audit identified **6 critical gaps** and **3 major gaps** that must be resolved before the Phase A Quality Gate can pass.

All fix specifications are in this directory (`skills/python-expert/fixes/`). Each file is self-contained: it describes the problem, provides the complete implementation, lists constraints, and gives a verification command.

**Backend root:** `airaad/backend/`
**This fixes directory:** `skills/python-expert/fixes/`

---

## EXECUTION ORDER

Execute each task **sequentially** in the order below. Do not skip ahead. Mark each task done before starting the next.

---

### STEP 1 — `TASK_FIX_C01.md` 🔴
**Create 3 Phase B stub task files**

Files to create:
- `airaad/backend/apps/vendors/tasks.py`
- `airaad/backend/apps/subscriptions/tasks.py`
- `airaad/backend/apps/tags/tasks.py`

**Why first:** Celery Beat crashes on startup without these files. Everything else depends on Beat running cleanly.

**Done when:** `celery -A celery_app inspect registered` lists all 3 task names without errors.

---

### STEP 2 — `TASK_FIX_M02.md` 🟠
**Implement `record_vendor_view()` fire-and-forget**

Files to create/update:
- Create: `airaad/backend/apps/analytics/tasks.py`
- Update: `airaad/backend/apps/analytics/services.py`

**Why second:** Creates a new task file before the factories and tests are written, so `TASK_FIX_C05` can test it.

**Done when:** `grep -n ".delay(" airaad/backend/apps/analytics/services.py` returns 1 match.

---

### STEP 3 — `TASK_FIX_M01.md` 🟠
**Fix N+1 query in `weekly_gps_drift_scan`**

File to update:
- `airaad/backend/apps/qa/tasks.py`

**Why third:** Fix the production performance bug before writing tests that exercise the task.

**Done when:** `grep -n "objects.get(id=vendor_id)" airaad/backend/apps/qa/tasks.py` returns no output.

---

### STEP 4 — `TASK_FIX_M03.md` 🟠
**Add PROMOTION + TIME tags to seed data**

File to update:
- `airaad/backend/apps/accounts/management/commands/seed_data.py`

**Why fourth:** Small isolated change with no test dependencies. Get it done before the test suite is written.

**Done when:** `python manage.py seed_data --no-vendors` prints 10 tags (2 each for LOCATION, CATEGORY, INTENT, TIME, PROMOTION).

---

### STEP 5 — `TASK_FIX_C02.md` 🔴
**Create `tests/factories.py`**

File to create:
- `airaad/backend/tests/factories.py`

**Why fifth:** Steps 6, 7, and 8 all import from `tests/factories.py`. This must exist before any test files are written.

**Done when:**
```bash
cd airaad/backend
python -c "
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
django.setup()
from tests.factories import AdminUserFactory, VendorFactory, ImportBatchFactory
print('OK')
"
```
prints `OK` without errors.

---

### STEP 6 — `TASK_FIX_C03.md` 🔴
**Create `tests/test_business_rules.py`**

File to create:
- `airaad/backend/tests/test_business_rules.py`

**Why sixth:** Business rule tests are foundational — they verify the architectural constraints that all other tests depend on.

**Done when:** `pytest tests/test_business_rules.py -v` passes with all 10 test classes present.

---

### STEP 7 — `TASK_FIX_C04.md` 🔴
**Create `tests/test_rbac.py`**

File to create:
- `airaad/backend/tests/test_rbac.py`

**Why seventh:** RBAC tests are independent of Celery task tests. Run them before the heavier moto-based tests.

**Done when:** `pytest tests/test_rbac.py -v` passes with 56+ parametrized test cases (7 roles × 8 endpoint groups).

---

### STEP 8 — `TASK_FIX_C05.md` 🔴
**Create `tests/test_celery_tasks.py`**

File to create:
- `airaad/backend/tests/test_celery_tasks.py`

**Why eighth:** Depends on factories (Step 5), the N+1 fix (Step 3), and the analytics task (Step 2) all being in place.

**Done when:** `pytest tests/test_celery_tasks.py -v` passes all S3 (moto) and QA (freezegun) tests.

---

### STEP 9 — `TASK_FIX_C06.md` 🔴
**Create `.github/workflows/ci.yml`**

File to create:
- `airaad/.github/workflows/ci.yml`

**Why last:** CI is the final gate. Write it only after all tests pass locally — the pipeline must be green on first push.

**Done when:**
```bash
python -c "import yaml; yaml.safe_load(open('airaad/.github/workflows/ci.yml'))" && echo "YAML valid"
```
prints `YAML valid`.

---

## FINAL VERIFICATION

Run this after all 9 steps are complete:

```bash
cd airaad/backend

# 1. Full test suite — must pass with ≥80% coverage
pytest --cov=. --cov-fail-under=80 --cov-report=term-missing -v

# 2. Beat starts without crash
celery -A celery_app inspect registered 2>&1 | grep -E "(discount_scheduler|subscription_expiry_check|hourly_tag_assignment)"

# 3. No psycopg2-binary in production
grep "psycopg2-binary" requirements/production.txt && echo "FAIL" || echo "PASS"

# 4. celery-beat replicas = 1
python -c "
import yaml
d = yaml.safe_load(open('../docker-compose.yml'))
r = d['services']['celery-beat']['deploy']['replicas']
print('celery-beat replicas:', r, '— PASS' if r == 1 else '— FAIL')
"

# 5. CI YAML is valid
python -c "import yaml; yaml.safe_load(open('../.github/workflows/ci.yml'))" && echo "CI YAML: PASS"
```

All 5 checks must pass before Phase A is considered complete.

---

## QUICK REFERENCE — BUSINESS RULES

| Rule | Constraint |
|------|-----------|
| R1 | `ST_Distance(geography=True)` — never degree × constant |
| R2 | AES-256-GCM for all phone numbers at rest |
| R3 | `RolePermission.for_roles()` — only RBAC mechanism |
| R4 | All business logic in `services.py` |
| R5 | `AuditLog` entry on every POST/PATCH/DELETE |
| R6 | Soft deletes only — `is_deleted=True` |
| R7 | `psycopg2` compiled — never `psycopg2-binary` in production |
| R8 | CSV never on Celery broker — `batch_id` only |
| R9 | `error_log` capped at 1000 entries |
| R10 | `celery-beat` `deploy.replicas: 1` — schedules in code |

## FORBIDDEN ACTIONS (apply to all files)

- NEVER use `psycopg2-binary` in `production.txt`
- NEVER use bare `except:` — always specific exception types
- NEVER use mutable default arguments (`def f(x=[])`)
- NEVER call `super().delete()` on soft-delete models
- NEVER write business logic in views or serializers
- NEVER use `datetime.now()` — always `django.utils.timezone.now()`
- NEVER store public S3 URLs — store S3 key only
- NEVER skip `log_action()` on any POST/PATCH/DELETE mutation
- NEVER use `JSONField(default=[])` — use `JSONField(default=list)`
- NEVER run real AWS/Redis/external API calls in tests — mock everything
