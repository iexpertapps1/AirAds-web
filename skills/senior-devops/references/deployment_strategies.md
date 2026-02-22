# Deployment Strategies — AirAd (Vercel + Railway)

## Overview

AirAd uses a split deployment model:
- **Vercel** — Frontend (React 18 + Vite), zero-config, CDN-backed
- **Railway** — Backend (Django), Celery worker, PostgreSQL + PostGIS, Redis

---

## Vercel — Frontend Deployment

### Initial Setup (One-Time)

```bash
cd airaad/frontend
npm i -g vercel
vercel login
vercel link          # Creates .vercel/project.json
vercel env add VITE_API_URL production
vercel env add VITE_APP_ENV production
```

### `vercel.json` (place in `airaad/frontend/`)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "framework": null,
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "geolocation=(self)" }
      ]
    }
  ]
}
```

### Deployment Flow

```
git push origin main
    └── Vercel webhook triggered
        ├── npm ci
        ├── npm run build (vite build)
        ├── Output: dist/ → CDN
        └── Production URL live in ~60s
```

### Environment Variables by Environment

| Variable | Development | Production |
|----------|-------------|------------|
| `VITE_API_URL` | `http://localhost:8000/api/v1` | `https://airaad.railway.app/api/v1` |
| `VITE_APP_ENV` | `development` | `production` |

> **Rule**: All frontend env vars must be prefixed with `VITE_` to be available at build time. Never put secrets in Vercel frontend env vars — they are public.

### Rollback on Vercel

```bash
# List deployments
vercel ls

# Promote a previous deployment to production
vercel promote <deployment-url>
```

---

## Railway — Backend Deployment

### Initial Setup (One-Time)

```bash
npm i -g @railway/cli
railway login
railway init          # Link to existing project or create new
```

### Service Architecture

```
Railway Project: airaad-production
├── backend (Django + Gunicorn)
│   ├── Source: GitHub repo, airaad/backend/
│   ├── Dockerfile: airaad/backend/Dockerfile
│   └── Start: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
├── celery (Celery Worker)
│   ├── Source: same repo
│   └── Start: celery -A config worker --loglevel=info
├── PostgreSQL (Plugin)
│   └── PostGIS extension enabled manually
└── Redis (Plugin)
```

### `railway.toml` (place in `airaad/backend/`)

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile -"
healthcheckPath = "/api/v1/health/"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### Required Environment Variables

```bash
# Set via Railway dashboard or CLI:
railway variables set DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
railway variables set DJANGO_SETTINGS_MODULE=config.settings.production
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=airaad-backend.railway.app
railway variables set CORS_ALLOWED_ORIGINS=https://airaad.vercel.app

# These are auto-injected by Railway plugins:
# DATABASE_URL  ← from PostgreSQL plugin
# REDIS_URL     ← from Redis plugin
```

### PostGIS One-Time Setup

```bash
railway run --service backend python manage.py dbshell
```
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
\q
```

### Deployment Flow

```
git push origin main
    └── Railway webhook triggered
        ├── Docker build (python:3.12-slim + GDAL)
        ├── pip install -r requirements/production.txt
        ├── collectstatic
        ├── Health check: GET /api/v1/health/ → 200
        └── Traffic switched to new container
```

### Migrations Strategy

**Never run migrations in Dockerfile or start command.** Run as a separate step:

```bash
# In GitHub Actions (after deploy):
railway run --service backend python manage.py migrate --noinput

# Or manually:
railway run python manage.py migrate --noinput
```

### Rollback on Railway

```bash
# Via dashboard: Deployments tab → click previous deployment → Rollback
# Via CLI:
railway rollback --service backend
```

---

## Zero-Downtime Deployment

Railway uses rolling deploys by default:
1. New container starts and passes health check
2. Traffic switches to new container
3. Old container stops

**Ensure health check endpoint is fast:**
```python
# airaad/backend/apps/core/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    connection.ensure_connection()
    return JsonResponse({"status": "ok"})
```

---

## Staging Environment

Recommended setup for pre-production testing:

```
Railway Project: airaad-staging
├── backend-staging (same Dockerfile, staging settings)
├── celery-staging
├── PostgreSQL-staging
└── Redis-staging

Vercel Project: airaad-staging
└── Connected to `develop` branch
```

GitHub Actions deploys staging on push to `develop`, production on push to `main`.

---

## Deployment Checklist

### Pre-Deploy
- [ ] All tests pass locally (`pytest` + `npm run test`)
- [ ] TypeScript compiles (`tsc --noEmit`)
- [ ] No pending migrations without corresponding code
- [ ] `DEBUG=False` verified in production settings
- [ ] `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` are correct

### Post-Deploy
- [ ] Health check endpoint returns 200
- [ ] Login flow works end-to-end
- [ ] Celery worker is processing tasks (check Railway logs)
- [ ] No 500 errors in Railway logs within 5 minutes of deploy
- [ ] Vercel deployment shows "Ready" status

### Rollback Triggers
- Health check fails after deploy
- Error rate > 1% in first 10 minutes
- Critical API endpoint returning 500
- Celery queue backing up unexpectedly

---

## Cost Optimization

| Service | Free Tier | Paid |
|---------|-----------|------|
| Vercel | Hobby (personal projects) | Pro $20/mo |
| Railway | $5 credit/mo | Usage-based ~$10-30/mo |
| Total | ~$0-5/mo dev | ~$30-50/mo production |

**Tips:**
- Use Railway's sleep mode for staging environments
- Vercel preview deployments are free on all plans
- Railway PostgreSQL storage is the main cost driver — archive old data
