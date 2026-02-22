# Senior DevOps Guidelines — AirAd

**Enforced rules for AI agents handling DevOps, deployment, and infrastructure tasks** for the AirAd platform.

Stack: Django 5.x + React 18 + Vite → **Railway** (backend) + **Vercel** (frontend) + **GitHub Actions** (CI/CD)

---

## Table of Contents

### Deployment — **CRITICAL**
1. [Never Deploy Without Passing Tests](#never-deploy-without-passing-tests)
2. [Environment Variable Rules](#environment-variable-rules)
3. [Migration Safety](#migration-safety)

### Security — **CRITICAL**
4. [Secret Management](#secret-management)
5. [Production Django Settings](#production-django-settings)

### CI/CD — **HIGH**
6. [GitHub Actions Pipeline Rules](#github-actions-pipeline-rules)
7. [Branch and Deploy Strategy](#branch-and-deploy-strategy)

### Docker — **HIGH**
8. [Dockerfile Rules](#dockerfile-rules)

### Platform-Specific — **HIGH**
9. [Railway Rules](#railway-rules)
10. [Vercel Rules](#vercel-rules)

---

## Deployment

### Never Deploy Without Passing Tests

**Impact: CRITICAL** | **Category: deployment** | **Tags:** ci, testing, gates

All CI jobs must pass before any deploy job runs. Deploy jobs must declare `needs: [backend-ci, frontend-ci]`.

#### ❌ Incorrect

```yaml
deploy-backend:
  runs-on: ubuntu-latest
  steps:
    - run: railway up
```

#### ✅ Correct

```yaml
deploy-backend:
  needs: [backend-ci, frontend-ci]
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  steps:
    - run: railway up --service ${{ secrets.RAILWAY_SERVICE_ID_BACKEND }} --detach
```

**Rules:**
- Deploy only on push to `main`, never on PRs
- Always gate deploys on both `backend-ci` AND `frontend-ci`
- Use `--detach` on Railway deploys to avoid GitHub Actions timeout
- Run `migrate` as a separate step AFTER deploy, never before

---

### Environment Variable Rules

**Impact: CRITICAL** | **Category: security** | **Tags:** env-vars, secrets, configuration

#### Rules (Never Break These)

1. **Never commit `.env` files** — must be in `.gitignore`
2. **Never hardcode secrets** in any file, Dockerfile, or workflow YAML
3. **Frontend env vars** must be prefixed with `VITE_` — they are public and bundled into the JS
4. **Never put secrets in Vercel env vars** — they are exposed to the browser
5. **Railway** injects `DATABASE_URL` and `REDIS_URL` automatically from plugins — never hardcode these
6. **Always maintain `.env.example`** with placeholder values for every real `.env` variable

#### ❌ Incorrect

```python
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "airaad",
        "USER": "airaad",
        "PASSWORD": "hardcoded_password",  # NEVER
    }
}
```

#### ✅ Correct

```python
import os
DATABASES = {"default": env.db("DATABASE_URL")}
```

#### Platform Variable Locations

| Variable | Platform | Set Via |
|----------|----------|---------|
| `DJANGO_SECRET_KEY` | Railway | Dashboard → Variables |
| `DATABASE_URL` | Railway | Auto-injected by PostgreSQL plugin |
| `REDIS_URL` | Railway | Auto-injected by Redis plugin |
| `VITE_API_URL` | Vercel | Dashboard → Environment Variables |
| `RAILWAY_TOKEN` | GitHub | Repo → Settings → Secrets → Actions |
| `VERCEL_TOKEN` | GitHub | Repo → Settings → Secrets → Actions |

---

### Migration Safety

**Impact: CRITICAL** | **Category: deployment** | **Tags:** database, migrations, safety

#### Rules

- **Never** run `migrate` in the Dockerfile `CMD` or `RUN`
- **Never** run `migrate` before the deploy completes
- **Always** run `migrate` as a separate GitHub Actions step after deploy
- **Always** make migrations backward-compatible (additive only, no column drops in same deploy)
- **Never** drop columns or rename columns in the same migration as code that uses the new schema

#### ✅ Correct Migration Step in CI

```yaml
- name: Run migrations
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
  run: railway run --service ${{ secrets.RAILWAY_SERVICE_ID_BACKEND }} python manage.py migrate --noinput
```

#### Safe Migration Pattern

```python
# Step 1: Add nullable column (deploy this first)
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name="vendor",
            name="new_field",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]

# Step 2: Backfill data (separate deploy)
# Step 3: Make field required (separate deploy)
```

---

## Security

### Secret Management

**Impact: CRITICAL** | **Category: security** | **Tags:** secrets, credentials, encryption

#### Rules

1. `DJANGO_SECRET_KEY` — minimum 50 random characters, rotate if ever exposed
2. `PHONE_ENCRYPTION_KEY` — must be 32 random bytes (AES-256-GCM requirement)
3. JWT signing keys — rotation invalidates all active sessions, plan accordingly
4. Never log secret values, even partially
5. Audit git history before open-sourcing: `git log --all -S "password"`

#### Generate Secrets

```bash
# Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# AES-256-GCM phone encryption key (32 bytes)
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Production Django Settings

**Impact: CRITICAL** | **Category: security** | **Tags:** django, production, hardening

Every production deployment MUST have these settings:

```python
DEBUG = False                              # NEVER True in production
SECURE_SSL_REDIRECT = True                 # Railway handles SSL termination
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
ALLOWED_HOSTS = ["airaad-backend.railway.app"]   # Exact domain, no wildcards
CORS_ALLOWED_ORIGINS = ["https://airaad.vercel.app"]  # Exact Vercel URL
```

#### ❌ Incorrect

```python
DEBUG = True          # In production
ALLOWED_HOSTS = ["*"] # Wildcard — never acceptable
CORS_ALLOW_ALL_ORIGINS = True  # Never in production
```

---

## CI/CD

### GitHub Actions Pipeline Rules

**Impact: HIGH** | **Category: ci-cd** | **Tags:** github-actions, pipeline, automation**

#### Required Job Structure

```
backend-ci  ──┐
               ├──► deploy-backend  (main only)
frontend-ci ──┘
               └──► deploy-frontend (main only)
```

#### Rules

- Use `postgis/postgis:16-3.4` (not plain `postgres`) in CI service containers
- Cache pip dependencies with `actions/setup-python@v5` `cache: pip`
- Cache npm with `actions/setup-node@v4` `cache: npm`
- Enforce coverage gate: `pytest --cov-fail-under=80`
- Run `tsc --noEmit` before frontend build
- Use `npm ci` (not `npm install`) in CI for reproducible installs
- Pin action versions with SHA or major version tags (`@v4`, not `@latest`)

#### ❌ Incorrect

```yaml
- uses: actions/checkout@latest  # Unpinned
- run: npm install               # Not reproducible
- run: pytest                    # No coverage gate
```

#### ✅ Correct

```yaml
- uses: actions/checkout@v4
- run: npm ci
- run: pytest --cov=. --cov-report=xml --cov-fail-under=80 -v
```

---

### Branch and Deploy Strategy

**Impact: HIGH** | **Category: ci-cd** | **Tags:** branching, gitflow, deployment**

| Branch | CI | Deploy |
|--------|----|--------|
| `main` | ✅ Full CI | ✅ Production (Railway + Vercel) |
| `develop` | ✅ Full CI | ✅ Staging (Railway staging + Vercel preview) |
| `feature/*` | ✅ Full CI | ✅ Vercel preview only (no backend) |
| PRs | ✅ Full CI | ❌ No deploy |

**Rules:**
- Feature branches merge to `develop`, not `main`
- `develop` merges to `main` via PR with required review
- Hotfixes branch from `main`, merge to both `main` and `develop`
- Never force-push to `main` or `develop`

---

## Docker

### Dockerfile Rules

**Impact: HIGH** | **Category: docker** | **Tags:** containerization, build, layers**

#### Rules

1. **Base image**: Always `python:3.12-slim` (not `python:3.12` — saves ~800MB)
2. **GDAL deps**: Must install `gdal-bin libgdal-dev libgeos-dev libproj-dev` for PostGIS
3. **Layer order**: System deps → Python deps → App code → collectstatic
4. **Never** `COPY .env .` into the image
5. **Never** use `ENV SECRET_KEY=...` in Dockerfile
6. **Always** `RUN rm -rf /var/lib/apt/lists/*` after apt-get
7. **Always** use `--no-install-recommends` with apt-get
8. **Never** run `migrate` in CMD or RUN
9. **Port**: Bind to `$PORT` (Railway injects this), not hardcoded `8000`

#### ❌ Incorrect

```dockerfile
FROM python:3.12
COPY .env .                    # Exposes secrets
ENV DJANGO_SECRET_KEY=abc123   # Secret in image
CMD python manage.py migrate && gunicorn ...  # Migrate in CMD
```

#### ✅ Correct

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev libgeos-dev libproj-dev libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:$PORT", "--workers", "2"]
```

#### `.dockerignore` (required)

```
.env
.env.*
!.env.example
__pycache__/
*.pyc
.git/
tests/
.pytest_cache/
.coverage
node_modules/
```

---

## Platform-Specific

### Railway Rules

**Impact: HIGH** | **Category: railway** | **Tags:** railway, backend, deployment**

1. **Always** set `healthcheckPath = "/api/v1/health/"` in `railway.toml`
2. **Always** deploy backend and celery as **separate Railway services**
3. **Never** hardcode `DATABASE_URL` or `REDIS_URL` — Railway injects them from plugins
4. **PostGIS**: Must run `CREATE EXTENSION IF NOT EXISTS postgis;` once after provisioning
5. **Port**: Django must bind to `$PORT` env var, not hardcoded 8000
6. **Logs**: Configure Django to log to stdout — Railway captures stdout automatically
7. **Restart policy**: Set `restartPolicyType = "ON_FAILURE"` with `maxRetries = 3`
8. **Celery**: Use `--concurrency=2` to stay within Railway's memory limits on starter plan

#### Health Check Endpoint (Required)

```python
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        connection.ensure_connection()
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "error"}, status=503)
```

---

### Vercel Rules

**Impact: HIGH** | **Category: vercel** | **Tags:** vercel, frontend, deployment**

1. **Always** add SPA rewrite: `{ "source": "/(.*)", "destination": "/index.html" }`
2. **Always** set immutable cache headers on `/assets/` (Vite hashes filenames)
3. **Never** put API secrets in Vercel env vars — they are bundled into public JS
4. **All** frontend env vars must be prefixed `VITE_` to be available at build time
5. **Framework**: Set `"framework": null` in `vercel.json` for Vite (not Next.js)
6. **Build output**: Must be `dist/` for Vite projects
7. **CORS**: Vercel domain must be added to Django's `CORS_ALLOWED_ORIGINS` exactly

#### ❌ Incorrect `vercel.json`

```json
{
  "framework": "nextjs",
  "outputDirectory": "build"
}
```

#### ✅ Correct `vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "framework": null,
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

---

## DevOps Behavior Rules

When acting as a senior DevOps engineer on this project:

1. **Always ask about environment** before writing deployment config — dev, staging, or production?
2. **Never suggest Kubernetes or Terraform** — Railway handles orchestration at this scale
3. **Always use `psycopg` (v3)**, never `psycopg2-binary` in production requirements
4. **Always validate** that `DEBUG=False` before any production deployment advice
5. **Always include rollback plan** when suggesting schema migrations
6. **Flag immediately** if any secret appears hardcoded anywhere in the codebase
7. **Prefer Railway CLI** for one-off commands, GitHub Actions for automated deploys
8. **Always separate** Celery worker as its own Railway service — never run in same process as Django

---

## Quick Reference Checklist

**Before First Production Deploy (CRITICAL)**
- [ ] `DEBUG=False` in production settings
- [ ] `DJANGO_SECRET_KEY` set in Railway (not in code)
- [ ] `DATABASE_URL` and `REDIS_URL` auto-injected from Railway plugins
- [ ] PostGIS extension enabled: `CREATE EXTENSION IF NOT EXISTS postgis;`
- [ ] Health check endpoint `/api/v1/health/` returns 200
- [ ] `ALLOWED_HOSTS` set to exact Railway domain
- [ ] `CORS_ALLOWED_ORIGINS` set to exact Vercel domain
- [ ] `.env` in `.gitignore`
- [ ] `.dockerignore` excludes `.env` and secrets

**GitHub Actions Setup (HIGH)**
- [ ] 6 secrets configured in GitHub repo settings
- [ ] `backend-ci` and `frontend-ci` jobs gate all deploy jobs
- [ ] `postgis/postgis:16-3.4` used in CI postgres service
- [ ] Coverage gate `--cov-fail-under=80` enforced
- [ ] Deploy only triggers on `main` push, not PRs

**Vercel Setup (HIGH)**
- [ ] `vercel.json` with SPA rewrite and security headers
- [ ] `VITE_API_URL` set to Railway backend URL
- [ ] Framework set to `null` (not `nextjs`)
- [ ] Output directory set to `dist`

---

## References

- [SKILL.md](SKILL.md) — Full DevOps toolkit overview
- [references/cicd_pipeline_guide.md](references/cicd_pipeline_guide.md) — Complete GitHub Actions workflows
- [references/deployment_strategies.md](references/deployment_strategies.md) — Vercel + Railway deployment details
- [references/infrastructure_as_code.md](references/infrastructure_as_code.md) — Docker + env management
