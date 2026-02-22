# CI/CD Pipeline Guide — AirAd (GitHub Actions)

## Overview

Complete GitHub Actions CI/CD setup for AirAd:
- **Backend**: Django 5.x + pytest → Railway
- **Frontend**: React 18 + Vite + vitest → Vercel
- Triggers: push to `main` (deploy), PRs (test only)

---

## Full CI/CD Workflow

### `.github/workflows/ci.yml`

```yaml
name: AirAd CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: "3.12"
  NODE_VERSION: "20"

jobs:
  # ─── Backend: Lint + Test ───────────────────────────────────────
  backend-ci:
    name: Backend CI
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_DB: airaad_test
          POSTGRES_USER: airaad
          POSTGRES_PASSWORD: testpassword
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    defaults:
      run:
        working-directory: airaad/backend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements/development.txt

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy .

      - name: Run tests
        env:
          DATABASE_URL: postgis://airaad:testpassword@localhost:5432/airaad_test
          REDIS_URL: redis://localhost:6379/0
          DJANGO_SETTINGS_MODULE: config.settings.test
          DJANGO_SECRET_KEY: ci-test-secret-key-not-for-production
        run: |
          pytest --cov=. --cov-report=xml --cov-fail-under=80 -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  # ─── Frontend: Lint + Test + Build ─────────────────────────────
  frontend-ci:
    name: Frontend CI
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: airaad/frontend

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: airaad/frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Run tests
        run: npm run test -- --run --coverage

      - name: Build
        env:
          VITE_API_URL: https://placeholder.railway.app/api/v1
          VITE_APP_ENV: ci
        run: npm run build

  # ─── Deploy Backend → Railway ───────────────────────────────────
  deploy-backend:
    name: Deploy Backend to Railway
    needs: [backend-ci, frontend-ci]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4

      - name: Install Railway CLI
        run: npm i -g @railway/cli

      - name: Deploy backend service
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service ${{ secrets.RAILWAY_SERVICE_ID_BACKEND }} --detach

      - name: Deploy celery worker
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway up --service ${{ secrets.RAILWAY_SERVICE_ID_CELERY }} --detach

      - name: Run migrations
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: railway run --service ${{ secrets.RAILWAY_SERVICE_ID_BACKEND }} python manage.py migrate --noinput

  # ─── Deploy Frontend → Vercel ───────────────────────────────────
  deploy-frontend:
    name: Deploy Frontend to Vercel
    needs: [backend-ci, frontend-ci]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm i -g vercel

      - name: Deploy to Vercel (Production)
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        working-directory: airaad/frontend
        run: vercel --prod --token=$VERCEL_TOKEN
```

---

## PR Preview Workflow

### `.github/workflows/preview.yml`

```yaml
name: Preview Deploy

on:
  pull_request:
    branches: [main, develop]

jobs:
  preview-frontend:
    name: Vercel Preview
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: airaad/frontend

    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm i -g vercel

      - name: Deploy Preview
        id: deploy
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          url=$(vercel --token=$VERCEL_TOKEN 2>&1 | tail -1)
          echo "preview_url=$url" >> $GITHUB_OUTPUT

      - name: Comment PR with preview URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 **Frontend Preview:** ${{ steps.deploy.outputs.preview_url }}'
            })
```

---

## Branch Protection Rules (GitHub Settings)

Configure on `main` branch:
```
✅ Require status checks to pass before merging
  - backend-ci
  - frontend-ci
✅ Require branches to be up to date before merging
✅ Require pull request reviews (1 reviewer)
✅ Dismiss stale pull request approvals when new commits are pushed
✅ Do not allow bypassing the above settings
```

---

## Required GitHub Secrets

| Secret | Where to Get |
|--------|-------------|
| `VERCEL_TOKEN` | Vercel Dashboard → Settings → Tokens |
| `VERCEL_ORG_ID` | `vercel whoami` or `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` after `vercel link` |
| `RAILWAY_TOKEN` | Railway Dashboard → Account → Tokens |
| `RAILWAY_SERVICE_ID_BACKEND` | Railway Dashboard → Service → Settings |
| `RAILWAY_SERVICE_ID_CELERY` | Railway Dashboard → Service → Settings |

---

## Pipeline Best Practices

### Do
- Run tests before any deploy step (`needs: [backend-ci, frontend-ci]`)
- Use `--detach` on Railway deploys to avoid timeout
- Run `migrate` as a separate step after deploy
- Cache pip and npm dependencies for speed
- Use `postgis/postgis` Docker image in CI (not plain postgres)
- Set `--cov-fail-under=80` to enforce coverage gate

### Don't
- Never deploy on PR — only on `main` push
- Never hardcode secrets in workflow YAML
- Never skip the build step before deploying frontend
- Never run migrations before the deploy completes
- Never use `latest` Docker image tags in CI services

---

## Workflow Execution Times (Target)

| Stage | Target |
|-------|--------|
| Backend lint + test | < 3 min |
| Frontend lint + test + build | < 2 min |
| Railway deploy | < 5 min |
| Vercel deploy | < 2 min |
| **Total (main push)** | **< 12 min** |
