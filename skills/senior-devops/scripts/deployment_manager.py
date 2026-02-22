#!/usr/bin/env python3
"""
Deployment Manager — AirAd

Checks deployment readiness for Railway (backend) and Vercel (frontend).
Validates environment variables, config files, and production settings.

Usage:
    python deployment_manager.py --check-env production
    python deployment_manager.py --check-env staging
    python deployment_manager.py --check-files
    python deployment_manager.py --check-all
    python deployment_manager.py --security-scan
    python deployment_manager.py --rollback-guide railway
    python deployment_manager.py --rollback-guide vercel
"""

import argparse
import json
import os
import sys
from pathlib import Path


REQUIRED_RAILWAY_ENV = [
    "DJANGO_SECRET_KEY",
    "DJANGO_SETTINGS_MODULE",
    "DATABASE_URL",
    "REDIS_URL",
    "ALLOWED_HOSTS",
    "CORS_ALLOWED_ORIGINS",
    "DEBUG",
]

REQUIRED_VERCEL_ENV = [
    "VITE_API_URL",
    "VITE_APP_ENV",
]

REQUIRED_GITHUB_SECRETS = [
    "VERCEL_TOKEN",
    "VERCEL_ORG_ID",
    "VERCEL_PROJECT_ID",
    "RAILWAY_TOKEN",
    "RAILWAY_SERVICE_ID_BACKEND",
    "RAILWAY_SERVICE_ID_CELERY",
]

REQUIRED_FILES = {
    "airaad/backend/Dockerfile": "Production Dockerfile for Railway",
    "airaad/backend/Dockerfile.dev": "Development Dockerfile",
    "airaad/backend/railway.toml": "Railway deployment config",
    "airaad/frontend/vercel.json": "Vercel deployment config",
    "airaad/backend/.env.example": "Backend env var documentation",
    "airaad/frontend/.env.example": "Frontend env var documentation",
    ".github/workflows/ci.yml": "GitHub Actions CI/CD workflow",
    "docker-compose.dev.yml": "Local development Docker Compose",
}

DANGEROUS_PRODUCTION_PATTERNS = [
    ("DEBUG=True", "DEBUG must be False in production"),
    ("DEBUG = True", "DEBUG must be False in production"),
    ('ALLOWED_HOSTS = ["*"]', "Wildcard ALLOWED_HOSTS is insecure"),
    ("ALLOWED_HOSTS = ['*']", "Wildcard ALLOWED_HOSTS is insecure"),
    ("CORS_ALLOW_ALL_ORIGINS = True", "CORS_ALLOW_ALL_ORIGINS must be False in production"),
    ("psycopg2-binary", "Use psycopg (v3) not psycopg2-binary in production"),
    ("COPY .env", "Never COPY .env into Docker image"),
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AirAd Deployment Manager — readiness checker and rollback guide",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deployment_manager.py --check-env production
  python deployment_manager.py --check-env staging
  python deployment_manager.py --check-files
  python deployment_manager.py --check-all
  python deployment_manager.py --security-scan
  python deployment_manager.py --rollback-guide railway
  python deployment_manager.py --rollback-guide vercel
        """,
    )
    parser.add_argument(
        "--check-env",
        choices=["production", "staging", "local"],
        metavar="ENV",
        help="Check environment variables for the given environment",
    )
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="Check that all required deployment files exist",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="Run all checks (files + env + security scan)",
    )
    parser.add_argument(
        "--security-scan",
        action="store_true",
        help="Scan codebase for dangerous production patterns",
    )
    parser.add_argument(
        "--rollback-guide",
        choices=["railway", "vercel"],
        metavar="PLATFORM",
        help="Print rollback instructions for the given platform",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser.parse_args()


def check_required_files(root: Path) -> dict:
    results: dict = {"passed": [], "failed": []}
    for rel_path, description in REQUIRED_FILES.items():
        full_path = root / rel_path
        if full_path.exists():
            results["passed"].append((rel_path, description))
        else:
            results["failed"].append((rel_path, description))
    return results


def check_env_vars(env: str) -> dict:
    results: dict = {
        "railway": {"present": [], "missing": []},
        "vercel": {"present": [], "missing": []},
        "github": {"required": REQUIRED_GITHUB_SECRETS},
    }
    current_env = dict(os.environ)
    for var in REQUIRED_RAILWAY_ENV:
        if var in current_env:
            results["railway"]["present"].append(var)
        else:
            results["railway"]["missing"].append(var)
    for var in REQUIRED_VERCEL_ENV:
        if var in current_env:
            results["vercel"]["present"].append(var)
        else:
            results["vercel"]["missing"].append(var)
    return results


def security_scan(root: Path) -> dict:
    issues: list[dict] = []
    scan_extensions = [".py", ".txt", ".toml", ".yml", ".yaml", "Dockerfile"]
    scanned = 0
    for ext in scan_extensions:
        pattern = f"*{ext}" if ext.startswith(".") else ext
        for file_path in root.rglob(pattern):
            if any(p in str(file_path) for p in [".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"]):
                continue
            try:
                content = file_path.read_text(errors="ignore")
                scanned += 1
                for pat, message in DANGEROUS_PRODUCTION_PATTERNS:
                    if pat in content:
                        issues.append({
                            "file": str(file_path.relative_to(root)),
                            "pattern": pat,
                            "message": message,
                        })
            except (PermissionError, OSError):
                continue
    return {"issues": issues, "files_scanned": scanned}


def print_file_check_results(results: dict) -> bool:
    print("\n── Required Deployment Files ──────────────────────────")
    for rel_path, description in results["passed"]:
        print(f"  ✅ {rel_path:<45} {description}")
    for rel_path, description in results["failed"]:
        print(f"  ❌ MISSING: {rel_path:<38} {description}")
    print()
    if not results["failed"]:
        print("✅ All required files present.")
        return True
    print(f"❌ {len(results['failed'])} file(s) missing.")
    return False


def print_env_check_results(results: dict, env: str) -> bool:
    print(f"\n── Environment Variables ({env}) ──────────────────────")
    print("\n  Railway (backend):")
    for var in results["railway"]["present"]:
        print(f"    ✅ {var}")
    for var in results["railway"]["missing"]:
        print(f"    ❌ NOT SET: {var}")
    print("\n  Vercel (frontend):")
    for var in results["vercel"]["present"]:
        print(f"    ✅ {var}")
    for var in results["vercel"]["missing"]:
        print(f"    ❌ NOT SET: {var}")
    print("\n  GitHub Secrets (set manually in repo settings):")
    for secret in results["github"]["required"]:
        print(f"    [ ] {secret}")
    missing_count = len(results["railway"]["missing"]) + len(results["vercel"]["missing"])
    print()
    if missing_count == 0:
        print("✅ All detectable env vars are set in current environment.")
        return True
    print("⚠️  Some env vars not found in current shell. Set them in Railway/Vercel dashboards.")
    return False


def print_security_scan_results(results: dict) -> bool:
    print(f"\n── Security Scan ({results['files_scanned']} files scanned) ──────────────")
    if not results["issues"]:
        print("  ✅ No dangerous patterns found.")
        return True
    for issue in results["issues"]:
        print(f"  ❌ {issue['file']}")
        print(f"     Pattern: {issue['pattern']!r}")
        print(f"     Issue:   {issue['message']}")
        print()
    print(f"❌ {len(results['issues'])} issue(s) found.")
    return False


def print_rollback_guide(platform: str) -> None:
    if platform == "railway":
        print("""
── Railway Rollback Guide ──────────────────────────────

Option 1: Via Railway Dashboard (Recommended)
  1. Go to railway.app → Your Project → backend service
  2. Click "Deployments" tab
  3. Find the last working deployment
  4. Click the three-dot menu → "Rollback to this deployment"
  5. Repeat for celery service if needed

Option 2: Via Railway CLI
  railway rollback --service backend
  railway rollback --service celery

Option 3: Force push previous commit
  git revert HEAD --no-edit
  git push origin main

After rollback:
  - Check health: curl https://your-backend.railway.app/api/v1/health/
  - Check logs:   railway logs --service backend
  - If migration ran: railway run --service backend python manage.py migrate <app> <prev>
""")
    elif platform == "vercel":
        print("""
── Vercel Rollback Guide ───────────────────────────────

Option 1: Via Vercel Dashboard (Recommended)
  1. Go to vercel.com → Your Project → Deployments
  2. Find the last working deployment (green checkmark)
  3. Click the three-dot menu → "Promote to Production"

Option 2: Via Vercel CLI
  vercel ls                          # List recent deployments
  vercel promote <deployment-url>    # Promote to production

Option 3: Git revert
  git revert HEAD --no-edit
  git push origin main               # Triggers new Vercel deploy

After rollback:
  - Verify production URL is live
  - Check browser console for errors
  - Confirm API calls reach Railway backend
""")


def main() -> None:
    args = parse_arguments()
    root = Path(args.root).resolve()

    if args.rollback_guide:
        print_rollback_guide(args.rollback_guide)
        return

    all_passed = True
    results_json: dict = {}

    if args.check_files or args.check_all:
        file_results = check_required_files(root)
        if args.output == "json":
            results_json["files"] = file_results
        else:
            ok = print_file_check_results(file_results)
            all_passed = all_passed and ok

    if args.check_env or args.check_all:
        env = args.check_env or "production"
        env_results = check_env_vars(env)
        if args.output == "json":
            results_json["env"] = env_results
        else:
            ok = print_env_check_results(env_results, env)
            all_passed = all_passed and ok

    if args.security_scan or args.check_all:
        scan_results = security_scan(root)
        if args.output == "json":
            results_json["security"] = scan_results
        else:
            ok = print_security_scan_results(scan_results)
            all_passed = all_passed and ok

    if args.output == "json":
        print(json.dumps(results_json, indent=2))
        return

    if not any([args.check_files, args.check_env, args.check_all, args.security_scan, args.rollback_guide]):
        print("No action specified. Run with --help for usage.")
        sys.exit(1)

    print()
    if all_passed:
        print("✅ All checks passed. Ready to deploy.")
    else:
        print("❌ Some checks failed. Fix issues before deploying.")
        sys.exit(1)


if __name__ == "__main__":
    main()
