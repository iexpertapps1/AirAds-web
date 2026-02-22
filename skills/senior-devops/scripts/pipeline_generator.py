#!/usr/bin/env python3
"""
Pipeline Generator — AirAd CI/CD

Generates GitHub Actions workflow YAML for the AirAd stack:
  - Backend: Django 5.x + pytest → Railway
  - Frontend: React 18 + Vite → Vercel

Usage:
    python pipeline_generator.py --output .github/workflows/ci.yml
    python pipeline_generator.py --validate .github/workflows/ci.yml
    python pipeline_generator.py --preview
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional


CI_WORKFLOW = """\
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
          python-version: ${{{{ env.PYTHON_VERSION }}}}
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
          node-version: ${{{{ env.NODE_VERSION }}}}
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
          RAILWAY_TOKEN: ${{{{ secrets.RAILWAY_TOKEN }}}}
        run: railway up --service ${{{{ secrets.RAILWAY_SERVICE_ID_BACKEND }}}} --detach

      - name: Deploy celery worker
        env:
          RAILWAY_TOKEN: ${{{{ secrets.RAILWAY_TOKEN }}}}
        run: railway up --service ${{{{ secrets.RAILWAY_SERVICE_ID_CELERY }}}} --detach

      - name: Run migrations
        env:
          RAILWAY_TOKEN: ${{{{ secrets.RAILWAY_TOKEN }}}}
        run: railway run --service ${{{{ secrets.RAILWAY_SERVICE_ID_BACKEND }}}} python manage.py migrate --noinput

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
          VERCEL_TOKEN: ${{{{ secrets.VERCEL_TOKEN }}}}
          VERCEL_ORG_ID: ${{{{ secrets.VERCEL_ORG_ID }}}}
          VERCEL_PROJECT_ID: ${{{{ secrets.VERCEL_PROJECT_ID }}}}
        working-directory: airaad/frontend
        run: vercel --prod --token=$VERCEL_TOKEN
"""

PREVIEW_WORKFLOW = """\
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
          VERCEL_TOKEN: ${{{{ secrets.VERCEL_TOKEN }}}}
          VERCEL_ORG_ID: ${{{{ secrets.VERCEL_ORG_ID }}}}
          VERCEL_PROJECT_ID: ${{{{ secrets.VERCEL_PROJECT_ID }}}}
        run: |
          url=$(vercel --token=$VERCEL_TOKEN 2>&1 | tail -1)
          echo "preview_url=$url" >> $GITHUB_OUTPUT

      - name: Comment PR with preview URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({{
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 **Frontend Preview:** ${{{{ steps.deploy.outputs.preview_url }}}}'
            }})
"""

REQUIRED_SECRETS = [
    "VERCEL_TOKEN",
    "VERCEL_ORG_ID",
    "VERCEL_PROJECT_ID",
    "RAILWAY_TOKEN",
    "RAILWAY_SERVICE_ID_BACKEND",
    "RAILWAY_SERVICE_ID_CELERY",
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AirAd GitHub Actions Pipeline Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline_generator.py --output .github/workflows/ci.yml
  python pipeline_generator.py --output .github/workflows/preview.yml --type preview
  python pipeline_generator.py --validate .github/workflows/ci.yml
  python pipeline_generator.py --preview
        """,
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Write workflow YAML to this file path",
    )
    parser.add_argument(
        "--type",
        choices=["ci", "preview"],
        default="ci",
        help="Workflow type to generate (default: ci)",
    )
    parser.add_argument(
        "--validate",
        type=str,
        metavar="FILE",
        help="Validate an existing workflow file for AirAd compliance",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print the generated workflow to stdout without writing",
    )
    parser.add_argument(
        "--secrets-checklist",
        action="store_true",
        help="Print the required GitHub Secrets checklist",
    )
    return parser.parse_args()


def get_workflow(workflow_type: str) -> str:
    if workflow_type == "preview":
        return PREVIEW_WORKFLOW
    return CI_WORKFLOW


def write_workflow(content: str, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"✅ Workflow written to: {path.absolute()}")


def validate_workflow(file_path: str) -> bool:
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    content = path.read_text()
    issues: list[str] = []
    warnings: list[str] = []

    checks = [
        ("postgis/postgis", "Using postgis/postgis image for CI postgres service"),
        ("--cov-fail-under=80", "Coverage gate enforced (--cov-fail-under=80)"),
        ("needs: [backend-ci, frontend-ci]", "Deploy jobs gated on CI jobs"),
        ("github.ref == 'refs/heads/main'", "Deploy only on main branch push"),
        ("npm ci", "Using npm ci (not npm install) for reproducible installs"),
        ("tsc --noEmit", "TypeScript type check included"),
        ("ruff check", "Python linting with ruff"),
        ("mypy", "Python type checking with mypy"),
        ("--detach", "Railway deploy uses --detach to avoid timeout"),
        ("migrate --noinput", "Migrations run after deploy"),
    ]

    print(f"\nValidating: {file_path}\n")
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ MISSING: {description}")
            issues.append(description)
            all_passed = False

    danger_patterns = [
        ("ALLOWED_HOSTS: \"*\"", "Wildcard ALLOWED_HOSTS detected"),
        ("DEBUG: True", "DEBUG=True in workflow env"),
        ("npm install", "Use npm ci instead of npm install in CI"),
    ]
    for pattern, description in danger_patterns:
        if pattern in content:
            print(f"  ⚠️  WARNING: {description}")
            warnings.append(description)

    print()
    if all_passed:
        print("✅ Workflow passes all AirAd compliance checks.")
    else:
        print(f"❌ {len(issues)} issue(s) found. See above.")

    return all_passed


def print_secrets_checklist() -> None:
    print("\nRequired GitHub Secrets for AirAd CI/CD:")
    print("=" * 50)
    print("Set via: GitHub repo → Settings → Secrets and variables → Actions\n")
    for secret in REQUIRED_SECRETS:
        print(f"  [ ] {secret}")
    print()
    print("Where to get them:")
    print("  VERCEL_TOKEN          → Vercel Dashboard → Settings → Tokens")
    print("  VERCEL_ORG_ID         → vercel whoami  OR  .vercel/project.json")
    print("  VERCEL_PROJECT_ID     → .vercel/project.json (after vercel link)")
    print("  RAILWAY_TOKEN         → Railway Dashboard → Account → Tokens")
    print("  RAILWAY_SERVICE_ID_*  → Railway Dashboard → Service → Settings")


def main() -> None:
    args = parse_arguments()

    if args.secrets_checklist:
        print_secrets_checklist()
        return

    if args.validate:
        ok = validate_workflow(args.validate)
        sys.exit(0 if ok else 1)

    workflow = get_workflow(args.type)

    if args.preview or not args.output:
        print(workflow)
        return

    if args.output:
        write_workflow(workflow, args.output)
        print("\nNext steps:")
        print("  1. Commit and push the workflow file")
        print("  2. Add required secrets to GitHub repo settings:")
        for secret in REQUIRED_SECRETS:
            print(f"     - {secret}")
        print("  3. Push to main branch to trigger first deploy")


if __name__ == "__main__":
    main()
