# Infrastructure & Environment Management — AirAd

## Overview

AirAd infrastructure is managed through:
- **Docker** — containerization for backend (local dev + Railway production)
- **Environment variables** — platform-native (Railway, Vercel, GitHub Secrets)
- **Docker Compose** — local development orchestration
- No Terraform/Kubernetes needed at this scale

---

## Docker

### Production Dockerfile (`airaad/backend/Dockerfile`)

```dockerfile
FROM python:3.12-slim

# Install GDAL/PostGIS system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### Development Dockerfile (`airaad/backend/Dockerfile.dev`)

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev libgeos-dev libproj-dev libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/development.txt .
RUN pip install --no-cache-dir -r development.txt

# No COPY . . — volume mount used in dev for hot reload
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose — Local Dev (`docker-compose.dev.yml`)

```yaml
version: "3.9"

services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: airaad_dev
      POSTGRES_USER: airaad
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U airaad"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./airaad/backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./airaad/backend:/app
    ports:
      - "8000:8000"
    env_file:
      - ./airaad/backend/.env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: python manage.py runserver 0.0.0.0:8000

  celery:
    build:
      context: ./airaad/backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./airaad/backend:/app
    env_file:
      - ./airaad/backend/.env
    depends_on:
      - backend
      - redis
    command: celery -A config worker --loglevel=info

volumes:
  postgres_data:
```

### Docker Best Practices

**Do:**
- Use multi-stage builds if image size is critical
- Install system deps before Python deps (better layer caching)
- Use `--no-install-recommends` to keep image lean
- Use `COPY requirements.txt .` before `COPY . .` for cache efficiency
- Run `collectstatic` in Dockerfile, not at runtime

**Don't:**
- Never store secrets in Dockerfile or Docker image layers
- Never use `latest` tag for base images in production
- Never run as root in production (add `USER` directive)
- Never run `migrate` in the Dockerfile CMD

---

## Environment Variable Management

### Hierarchy (Priority Order)

```
1. Platform env vars (Railway / Vercel dashboard)  ← highest priority
2. GitHub Secrets                                   ← CI/CD only
3. .env file (local dev only)                       ← never committed
4. .env.example                                     ← committed, no real values
```

### `.env.example` (`airaad/backend/.env.example`)

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (auto-injected by Railway in production)
DATABASE_URL=postgis://airaad:devpassword@localhost:5432/airaad_dev

# Redis (auto-injected by Railway in production)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Phone encryption (AES-256-GCM)
PHONE_ENCRYPTION_KEY=32-byte-hex-key-here
```

### `.env.example` (`airaad/frontend/.env.example`)

```bash
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_ENV=development
```

### Platform-Specific Variable Management

#### Railway
```bash
# List all variables
railway variables list

# Set a variable
railway variables set KEY=VALUE

# Set for specific service
railway variables set KEY=VALUE --service backend

# Import from .env file (dev only, never production)
railway variables import .env
```

#### Vercel
```bash
# Add variable interactively
vercel env add VITE_API_URL

# Add for specific environment
vercel env add VITE_API_URL production
vercel env add VITE_API_URL preview
vercel env add VITE_API_URL development

# List all variables
vercel env ls

# Pull to local .env.local
vercel env pull .env.local
```

#### GitHub Actions Secrets
Set via: `GitHub repo → Settings → Secrets and variables → Actions → New repository secret`

Required secrets:
```
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
RAILWAY_TOKEN
RAILWAY_SERVICE_ID_BACKEND
RAILWAY_SERVICE_ID_CELERY
```

---

## Django Settings Structure

```
config/settings/
├── base.py          # Shared settings
├── development.py   # Local dev (DEBUG=True, console email)
├── test.py          # CI test settings (in-memory cache, fast passwords)
└── production.py    # Production (DEBUG=False, strict security)
```

### `production.py` Key Settings

```python
from .base import *
import os

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"

# CORS
CORS_ALLOWED_ORIGINS = os.environ["CORS_ALLOWED_ORIGINS"].split(",")
CORS_ALLOW_CREDENTIALS = True

# Static files (WhiteNoise)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Logging to stdout (Railway captures it)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
```

---

## Requirements Structure

```
requirements/
├── base.txt         # Core dependencies (Django, DRF, etc.)
├── development.txt  # -r base.txt + dev tools (ruff, mypy, pytest)
├── production.txt   # -r base.txt + production tools (gunicorn, whitenoise)
└── test.txt         # -r development.txt + test-specific packages
```

### `production.txt` essentials

```
-r base.txt
gunicorn==21.x
whitenoise[brotli]==6.x
psycopg[binary]==3.x        # Note: psycopg3, NOT psycopg2-binary
sentry-sdk[django]==2.x     # Error tracking
```

> **Critical**: Use `psycopg` (v3), NOT `psycopg2-binary` in production per project constraints.

---

## Security Checklist

### Secrets
- [ ] No secrets in git history (`git log --all -S "secret"`)
- [ ] `.env` in `.gitignore`
- [ ] `DJANGO_SECRET_KEY` is 50+ random characters
- [ ] `PHONE_ENCRYPTION_KEY` is 32 random bytes (AES-256-GCM)
- [ ] JWT keys not hardcoded

### Network
- [ ] `ALLOWED_HOSTS` does not contain `*` in production
- [ ] `CORS_ALLOWED_ORIGINS` is exact Vercel URL, not wildcard
- [ ] Railway service not publicly exposed except backend port

### Docker
- [ ] No `COPY .env .` in Dockerfile
- [ ] No secrets in `ENV` instructions in Dockerfile
- [ ] `.dockerignore` excludes `.env`, `*.pyc`, `__pycache__`, `.git`

### `.dockerignore`
```
.env
.env.*
!.env.example
__pycache__/
*.pyc
*.pyo
.git/
.gitignore
*.md
tests/
.pytest_cache/
.coverage
htmlcov/
node_modules/
```
