#!/usr/bin/env python3
"""
Env Validator — AirAd

Validates .env and .env.example files for completeness and correctness.
Checks that all required variables are documented, no secrets are committed,
and no variables are missing between .env and .env.example.

Note: This file is named terraform_scaffolder.py for legacy compatibility.
      Terraform is NOT used in the AirAd stack (Railway handles orchestration).

Usage:
    python terraform_scaffolder.py --check-backend
    python terraform_scaffolder.py --check-frontend
    python terraform_scaffolder.py --check-all
    python terraform_scaffolder.py --diff airaad/backend/.env airaad/backend/.env.example
    python terraform_scaffolder.py --generate-example airaad/backend/.env
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


BACKEND_REQUIRED_VARS = [
    "DJANGO_SECRET_KEY",
    "DJANGO_SETTINGS_MODULE",
    "DEBUG",
    "ALLOWED_HOSTS",
    "DATABASE_URL",
    "REDIS_URL",
    "CORS_ALLOWED_ORIGINS",
    "JWT_ACCESS_TOKEN_LIFETIME_MINUTES",
    "JWT_REFRESH_TOKEN_LIFETIME_DAYS",
    "PHONE_ENCRYPTION_KEY",
]

FRONTEND_REQUIRED_VARS = [
    "VITE_API_URL",
    "VITE_APP_ENV",
]

SECRET_PATTERNS = [
    (r"SECRET_KEY\s*=\s*['\"]?[a-zA-Z0-9+/]{20,}", "Possible real Django SECRET_KEY"),
    (r"PASSWORD\s*=\s*['\"]?(?!your|change|example|placeholder|xxx)[a-zA-Z0-9]{6,}", "Possible real password"),
    (r"TOKEN\s*=\s*['\"]?[a-zA-Z0-9_\-]{20,}", "Possible real token"),
    (r"KEY\s*=\s*['\"]?[a-f0-9]{32,}", "Possible real hex key (AES/API key)"),
]

PLACEHOLDER_VALUES = {
    "DJANGO_SECRET_KEY": "your-secret-key-here",
    "DATABASE_URL": "postgis://airaad:devpassword@localhost:5432/airaad_dev",
    "REDIS_URL": "redis://localhost:6379/0",
    "PHONE_ENCRYPTION_KEY": "32-byte-hex-key-here",
    "VITE_API_URL": "http://localhost:8000/api/v1",
    "VITE_APP_ENV": "development",
    "DEBUG": "True",
    "ALLOWED_HOSTS": "localhost,127.0.0.1",
    "CORS_ALLOWED_ORIGINS": "http://localhost:5173",
    "DJANGO_SETTINGS_MODULE": "config.settings.development",
    "JWT_ACCESS_TOKEN_LIFETIME_MINUTES": "60",
    "JWT_REFRESH_TOKEN_LIFETIME_DAYS": "7",
}


def parse_env_file(file_path: Path) -> dict[str, str]:
    """Parse a .env file into a dict of key → value."""
    if not file_path.exists():
        return {}
    vars_: dict[str, str] = {}
    for line in file_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            vars_[key.strip()] = value.strip().strip("'\"")
    return vars_


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AirAd Env Validator — validates .env and .env.example files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python terraform_scaffolder.py --check-backend
  python terraform_scaffolder.py --check-frontend
  python terraform_scaffolder.py --check-all
  python terraform_scaffolder.py --diff airaad/backend/.env airaad/backend/.env.example
  python terraform_scaffolder.py --generate-example airaad/backend/.env
        """,
    )
    parser.add_argument("--check-backend", action="store_true", help="Validate backend .env.example")
    parser.add_argument("--check-frontend", action="store_true", help="Validate frontend .env.example")
    parser.add_argument("--check-all", action="store_true", help="Validate both backend and frontend")
    parser.add_argument("--diff", nargs=2, metavar=("ENV_FILE", "EXAMPLE_FILE"),
                        help="Compare .env against .env.example for missing/extra vars")
    parser.add_argument("--generate-example", metavar="ENV_FILE",
                        help="Generate a .env.example from an existing .env (replaces values with placeholders)")
    parser.add_argument("--scan-secrets", metavar="ENV_FILE",
                        help="Scan a .env.example for accidentally committed real secrets")
    parser.add_argument("--root", type=str, default=".", help="Project root (default: .)")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    return parser.parse_args()


def check_env_example(example_path: Path, required_vars: list[str], label: str) -> bool:
    print(f"\n── {label} ({example_path}) ──────────────────────────")
    if not example_path.exists():
        print(f"  ❌ File not found: {example_path}")
        return False

    documented = parse_env_file(example_path)
    all_ok = True

    for var in required_vars:
        if var in documented:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ MISSING: {var}")
            all_ok = False

    extra = [k for k in documented if k not in required_vars]
    if extra:
        print(f"\n  ℹ️  Extra vars (not in required list, may be intentional):")
        for k in extra:
            print(f"     {k}")

    print()
    if all_ok:
        print(f"✅ {label}: all required vars documented.")
    else:
        print(f"❌ {label}: missing vars in .env.example.")
    return all_ok


def diff_env_files(env_path: Path, example_path: Path) -> bool:
    print(f"\n── Diff: {env_path} vs {example_path} ──────────────")
    env_vars = parse_env_file(env_path)
    example_vars = parse_env_file(example_path)

    in_env_not_example = set(env_vars) - set(example_vars)
    in_example_not_env = set(example_vars) - set(env_vars)

    all_ok = True

    if in_env_not_example:
        print(f"\n  ⚠️  In .env but NOT in .env.example (undocumented):")
        for k in sorted(in_env_not_example):
            print(f"     {k}")
        all_ok = False
    else:
        print("  ✅ All .env vars are documented in .env.example")

    if in_example_not_env:
        print(f"\n  ℹ️  In .env.example but NOT in .env (may need to be set locally):")
        for k in sorted(in_example_not_env):
            print(f"     {k}")

    print()
    return all_ok


def scan_for_secrets(example_path: Path) -> bool:
    print(f"\n── Secret Scan: {example_path} ──────────────────────")
    if not example_path.exists():
        print(f"  ❌ File not found: {example_path}")
        return False

    content = example_path.read_text()
    issues: list[str] = []

    for pattern, description in SECRET_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"{description}: {matches[0][:20]}...")

    if not issues:
        print("  ✅ No suspicious secret patterns found in .env.example")
        return True

    for issue in issues:
        print(f"  ⚠️  {issue}")
    print(f"\n❌ {len(issues)} potential secret(s) found. Replace with placeholder values.")
    return False


def generate_example(env_path: Path) -> None:
    env_vars = parse_env_file(env_path)
    if not env_vars:
        print(f"❌ Could not read {env_path}")
        return

    example_path = env_path.parent / ".env.example"
    lines = [f"# Auto-generated from {env_path.name} — replace values with placeholders\n"]

    for key in env_vars:
        placeholder = PLACEHOLDER_VALUES.get(key, f"your-{key.lower().replace('_', '-')}-here")
        lines.append(f"{key}={placeholder}")

    example_path.write_text("\n".join(lines) + "\n")
    print(f"✅ Generated: {example_path}")
    print("⚠️  Review the file and ensure no real secrets were included.")


def main() -> None:
    args = parse_arguments()
    root = Path(args.root).resolve()
    all_passed = True

    if args.generate_example:
        generate_example(Path(args.generate_example))
        return

    if args.scan_secrets:
        ok = scan_for_secrets(Path(args.scan_secrets))
        sys.exit(0 if ok else 1)

    if args.diff:
        ok = diff_env_files(Path(args.diff[0]), Path(args.diff[1]))
        sys.exit(0 if ok else 1)

    if args.check_backend or args.check_all:
        ok = check_env_example(
            root / "airaad/backend/.env.example",
            BACKEND_REQUIRED_VARS,
            "Backend .env.example",
        )
        all_passed = all_passed and ok

    if args.check_frontend or args.check_all:
        ok = check_env_example(
            root / "airaad/frontend/.env.example",
            FRONTEND_REQUIRED_VARS,
            "Frontend .env.example",
        )
        all_passed = all_passed and ok

    if not any([args.check_backend, args.check_frontend, args.check_all,
                args.diff, args.generate_example, args.scan_secrets]):
        print("No action specified. Run with --help for usage.")
        sys.exit(1)

    print()
    if all_passed:
        print("✅ All env checks passed.")
    else:
        print("❌ Some env checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
