# TASK_FIX_C06 — Create `.github/workflows/ci.yml`
**Severity:** 🔴 CRITICAL — Phase A Quality Gate requires a passing CI pipeline
**Session:** A-S8 | **Effort:** 30 min | **Depends on:** All other fixes (tests must pass first)

---

## PROBLEM

No `.github/` directory exists. The Phase A Quality Gate requires a full CI pipeline with lint, migration check, test (≥80% coverage), security scan, and frontend build jobs.

---

## FILE TO CREATE

**`.github/workflows/ci.yml`**
(relative to `airaad/` — i.e., `airaad/.github/workflows/ci.yml`)

---

## COMPLETE IMPLEMENTATION

```yaml
name: AirAd CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.12"
  NODE_VERSION: "20"

jobs:
  # -------------------------------------------------------------------------
  # Job 1: Python lint
  # -------------------------------------------------------------------------
  lint:
    name: Python Lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: airaad/backend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install lint tools
        run: pip install flake8 isort black

      - name: flake8
        run: flake8 apps/ core/ config/ celery_app.py --max-line-length=88 --extend-ignore=E203,W503

      - name: isort
        run: isort --check-only --diff apps/ core/ config/ celery_app.py

      - name: black
        run: black --check --diff apps/ core/ config/ celery_app.py

  # -------------------------------------------------------------------------
  # Job 2: Migration check
  # -------------------------------------------------------------------------
  migration-check:
    name: Migration Check
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: airaad/backend
    services:
      postgres:
        image: postgis/postgis:16-3.4-alpine
        env:
          POSTGRES_DB: test_airaad_db
          POSTGRES_USER: airaad
          POSTGRES_PASSWORD: airaad
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    env:
      DJANGO_SETTINGS_MODULE: config.settings.test
      SECRET_KEY: ci-test-secret-key-not-for-production
      ENCRYPTION_KEY: YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE=
      DATABASE_URL: postgis://airaad:airaad@localhost:5432/test_airaad_db
      REDIS_URL: redis://localhost:6379/0
      AWS_ACCESS_KEY_ID: test-key
      AWS_SECRET_ACCESS_KEY: test-secret
      AWS_STORAGE_BUCKET_NAME: test-bucket
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install GDAL
        run: sudo apt-get update && sudo apt-get install -y gdal-bin libgdal-dev

      - name: Install dependencies
        run: pip install -r requirements/test.txt

      - name: Check for missing migrations
        run: python manage.py migrate --check

  # -------------------------------------------------------------------------
  # Job 3: Test suite (≥80% coverage required)
  # -------------------------------------------------------------------------
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: airaad/backend
    services:
      postgres:
        image: postgis/postgis:16-3.4-alpine
        env:
          POSTGRES_DB: test_airaad_db
          POSTGRES_USER: airaad
          POSTGRES_PASSWORD: airaad
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    env:
      DJANGO_SETTINGS_MODULE: config.settings.test
      SECRET_KEY: ci-test-secret-key-not-for-production
      ENCRYPTION_KEY: YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE=
      DATABASE_URL: postgis://airaad:airaad@localhost:5432/test_airaad_db
      REDIS_URL: redis://localhost:6379/0
      AWS_ACCESS_KEY_ID: test-key
      AWS_SECRET_ACCESS_KEY: test-secret
      AWS_STORAGE_BUCKET_NAME: test-bucket
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install GDAL
        run: sudo apt-get update && sudo apt-get install -y gdal-bin libgdal-dev

      - name: Install dependencies
        run: pip install -r requirements/test.txt

      - name: Run migrations
        run: python manage.py migrate --noinput

      - name: Run tests with coverage
        run: pytest --cov=. --cov-fail-under=80 --cov-report=xml --cov-report=term-missing -v

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: airaad/backend/coverage.xml
          fail_ci_if_error: false

  # -------------------------------------------------------------------------
  # Job 4: Security scan
  # -------------------------------------------------------------------------
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: airaad/backend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install security tools
        run: pip install bandit safety

      - name: bandit — static security analysis
        run: bandit -r apps/ core/ -ll --format txt

      - name: safety — dependency vulnerability check
        run: safety check -r requirements/production.txt

  # -------------------------------------------------------------------------
  # Job 5: Frontend lint
  # -------------------------------------------------------------------------
  frontend-lint:
    name: Frontend Lint
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: airaad/frontend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: airaad/frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: ESLint
        run: npm run lint

      - name: TypeScript type check
        run: npm run type-check

  # -------------------------------------------------------------------------
  # Job 6: Frontend build
  # -------------------------------------------------------------------------
  frontend-build:
    name: Frontend Build
    runs-on: ubuntu-latest
    needs: [frontend-lint]
    defaults:
      run:
        working-directory: airaad/frontend
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: airaad/frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          VITE_API_BASE_URL: http://localhost:8000
```

---

## CONSTRAINTS

- **`ENCRYPTION_KEY`** in CI env must be a valid base64-encoded 32-byte string — the value `YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE=` decodes to 32 `a` bytes — safe for CI only
- **`--cov-fail-under=80`** in the `test` job is non-negotiable — CI must fail if coverage drops below 80%
- **`postgis/postgis:16-3.4-alpine`** — must match the production PostgreSQL version exactly
- **`redis:7-alpine`** — must match `requirements/base.txt` Redis client version
- **`working-directory: airaad/backend`** — all Python jobs run from the backend root, not the repo root
- **`working-directory: airaad/frontend`** — all Node jobs run from the frontend root
- **`frontend-build` needs `frontend-lint`** — build only runs if lint passes
- The `test` job does NOT need `lint` or `migration-check` as prerequisites — they run in parallel for speed
- **Do NOT** add `SECRET_KEY` or `ENCRYPTION_KEY` to GitHub Secrets for CI — the test values are intentionally non-secret placeholders

---

## VERIFICATION

```bash
# Validate YAML syntax locally
python -c "import yaml; yaml.safe_load(open('airaad/.github/workflows/ci.yml'))" && echo "YAML valid"

# Check the file exists at the correct path
ls -la airaad/.github/workflows/ci.yml

# Simulate what GitHub Actions would see
cat airaad/.github/workflows/ci.yml | grep "name:" | head -20
```

---

## PYTHON EXPERT RULES APPLIED

- **Correctness:** `--health-cmd` options on services prevent tests running before DB is ready
- **Performance:** `cache: pip` and `cache: npm` reduce CI run time significantly
- **Style:** Each job has a human-readable `name:` field; section comments separate jobs
