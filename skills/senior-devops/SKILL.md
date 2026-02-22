---
name: senior-devops
description: Senior DevOps skill for AirAd platform. Covers CI/CD with GitHub Actions, frontend deployment to Vercel, backend deployment to Railway (Django + PostgreSQL + Redis), Docker containerization, environment variable management, and production readiness. Use when setting up pipelines, deploying to Vercel or Railway, configuring GitHub Actions, managing secrets, or troubleshooting deployment issues.
---

# Senior DevOps — AirAd Platform

Deployment and CI/CD toolkit for AirAd's stack:
- **Frontend** (React 18 + Vite + TypeScript) → **Vercel**
- **Backend** (Django 5.x + DRF + Celery) → **Railway**
- **Database** → **Railway PostgreSQL + PostGIS**
- **Cache/Queue** → **Railway Redis**
- **CI/CD** → **GitHub Actions**
- **Containers** → **Docker + Docker Compose**

---

## Quick Start

### Deploy Frontend to Vercel
```bash
# Via CLI
npm i -g vercel
vercel --prod

# Or connect GitHub repo in Vercel dashboard → auto-deploys on push to main
```

### Deploy Backend to Railway
```bash
# Via CLI
npm i -g @railway/cli
railway login
railway up
```

### Run CI/CD Pipeline Locally
```bash
# Validate GitHub Actions workflow syntax
python scripts/pipeline_generator.py --validate .github/workflows/

# Check deployment readiness
python scripts/deployment_manager.py --check-env production
```

---

## Architecture Overview

```
GitHub (main branch push)
    │
    ├── GitHub Actions CI
    │     ├── Run Django tests (pytest)
    │     ├── Run React tests (vitest)
    │     ├── Lint + type-check
    │     └── Build Docker image
    │
    ├── Vercel (auto-deploy frontend)
    │     ├── Build: vite build
    │     ├── Output: dist/
    │     └── Env: VITE_API_URL → Railway backend URL
    │
    └── Railway (auto-deploy backend)
          ├── Django app (Gunicorn)
          ├── Celery worker
          ├── PostgreSQL + PostGIS
          └── Redis
```

---

## Vercel — Frontend Deployment

### Project Configuration (`vercel.json`)
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

### Required Environment Variables (Vercel Dashboard)
```
VITE_API_URL=https://your-backend.railway.app/api/v1
VITE_APP_ENV=production
```

### Branch Strategy
- `main` → Production deployment (auto)
- `develop` → Preview deployment (auto)
- Feature branches → Preview deployment (auto on PR)

---

## Railway — Backend Deployment

### Service Layout
```
Railway Project: airaad
├── Service: backend      (Django + Gunicorn)
├── Service: celery       (Celery worker)
├── Plugin: PostgreSQL    (with PostGIS extension)
└── Plugin: Redis
```

### `railway.toml`
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
healthcheckPath = "/api/v1/health/"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Required Environment Variables (Railway Dashboard)
```
DJANGO_SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DJANGO_SETTINGS_MODULE=config.settings.production
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
ALLOWED_HOSTS=your-backend.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
```

### PostGIS Setup (Railway PostgreSQL)
```bash
# Run once after Railway PostgreSQL is provisioned
railway run python manage.py dbshell
# Then in psql:
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

### Celery Worker Service
```toml
# Separate Railway service for Celery
[deploy]
startCommand = "celery -A config worker --loglevel=info --concurrency=2"
```

---

## GitHub Actions CI/CD

See full workflow in `references/cicd_pipeline_guide.md`.

### Pipeline Stages
1. **Lint & Type Check** — ruff, mypy (backend), tsc, eslint (frontend)
2. **Test** — pytest with coverage (backend), vitest (frontend)
3. **Build** — Docker image build (backend), vite build (frontend)
4. **Deploy** — Vercel CLI (frontend), Railway CLI (backend) on `main` push only

### Required GitHub Secrets
```
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
RAILWAY_TOKEN
RAILWAY_SERVICE_ID_BACKEND
RAILWAY_SERVICE_ID_CELERY
```

---

## Docker

### Production Dockerfile (Backend)
```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev libgeos-dev libproj-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### Local Development
```bash
docker-compose -f docker-compose.dev.yml up --build
```

---

## Environment Variable Management

### Rules
1. **Never commit `.env` files** — always in `.gitignore`
2. **Use `.env.example`** with placeholder values for documentation
3. **Vercel** — set via dashboard or `vercel env add`
4. **Railway** — set via dashboard or `railway variables set KEY=VALUE`
5. **GitHub Actions** — set via repo Settings → Secrets and Variables → Actions
6. **Local dev** — `.env` file loaded by Django's `python-decouple` or `django-environ`

### Secret Rotation Checklist
- [ ] `DJANGO_SECRET_KEY` — rotate if exposed, invalidates all sessions
- [ ] `DATABASE_URL` — rotate via Railway dashboard, update all services
- [ ] JWT signing keys — rotate requires all users to re-login
- [ ] Third-party API keys — rotate in provider dashboard first, then update Railway

---

## Scripts

### `scripts/pipeline_generator.py`
Generates GitHub Actions workflow YAML for the AirAd stack.
```bash
python scripts/pipeline_generator.py --output .github/workflows/ci.yml
python scripts/pipeline_generator.py --validate .github/workflows/ci.yml
```

### `scripts/deployment_manager.py`
Checks deployment readiness and manages Railway/Vercel deployments.
```bash
python scripts/deployment_manager.py --check-env production
python scripts/deployment_manager.py --rollback railway --service backend
```

### `scripts/env_validator.py`
Validates that all required environment variables are set.
```bash
python scripts/env_validator.py --platform railway
python scripts/env_validator.py --platform vercel
```

---

## Production Readiness Checklist

### Before First Deploy
- [ ] `DEBUG=False` in production settings
- [ ] `ALLOWED_HOSTS` set to Railway domain
- [ ] `CORS_ALLOWED_ORIGINS` set to Vercel domain only
- [ ] `DJANGO_SECRET_KEY` is random and not in version control
- [ ] PostGIS extension enabled on Railway PostgreSQL
- [ ] Static files served via WhiteNoise or CDN
- [ ] `collectstatic` runs in Dockerfile
- [ ] Health check endpoint `/api/v1/health/` returns 200
- [ ] Celery worker service deployed separately on Railway
- [ ] Redis URL configured for both Django cache and Celery broker

### Security
- [ ] HTTPS enforced (Vercel and Railway do this automatically)
- [ ] `SECURE_SSL_REDIRECT=True` in Django production settings
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] No secrets in Docker image layers
- [ ] `.env` in `.gitignore`

### Monitoring
- [ ] Railway metrics dashboard reviewed
- [ ] Vercel analytics enabled
- [ ] Django logging configured to stdout (Railway captures it)
- [ ] Celery task failure alerts configured

---

## Troubleshooting

### Railway Deploy Fails
```bash
# Check logs
railway logs --service backend

# Common causes:
# 1. Missing env var → check railway variables list
# 2. PostGIS not installed → run CREATE EXTENSION postgis in dbshell
# 3. collectstatic fails → check STATIC_ROOT setting
# 4. Port binding → ensure app binds to $PORT not hardcoded 8000
```

### Vercel Build Fails
```bash
# Common causes:
# 1. VITE_API_URL not set → add in Vercel dashboard
# 2. TypeScript errors → run tsc --noEmit locally first
# 3. Missing env var at build time → prefix with VITE_
```

### GitHub Actions Fails
```bash
# Common causes:
# 1. Missing secret → check repo Settings → Secrets
# 2. Railway token expired → regenerate in Railway dashboard
# 3. Test failures → run pytest locally with same env
```

---

## Reference Documentation

- **CI/CD Workflows**: `references/cicd_pipeline_guide.md`
- **Deployment Strategies**: `references/deployment_strategies.md`
- **Infrastructure & Env Management**: `references/infrastructure_as_code.md`
- **AGENTS.md**: Enforced DevOps rules for Windsurf
