#!/usr/bin/env bash
# =============================================================================
# AirAd — Production Deploy (Master Script)
# =============================================================================
# Commits pending fixes, verifies production readiness, and triggers the
# production deployment via GitHub Actions.
#
# Flow:
#   1. Commit & push pending bug fixes to main
#   2. Verify all infrastructure prerequisites are met
#   3. Push triggers CI → deploy-production.yml automatically
#   4. Monitor deployment status
#
# Prerequisites (run these first if not done):
#   ./scripts/setup-railway-prod.sh
#   ./scripts/setup-vercel-prod.sh
#   ./scripts/setup-github-secrets.sh
#
# Usage:
#   chmod +x scripts/deploy-production.sh
#   ./scripts/deploy-production.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO="iexpertapps/AirAds-web"

echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AirAd — Production Deploy${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""

# ---------------------------------------------------------------------------
# Phase 1: Pre-deploy checks
# ---------------------------------------------------------------------------
echo -e "${CYAN}Phase 1: Pre-deploy Checks${NC}"
echo -e "${CYAN}──────────────────────────${NC}"

# Check branch
CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    echo -e "${RED}✗ Must be on 'main' branch. Currently on: $CURRENT_BRANCH${NC}"
    exit 1
fi
echo -e "${GREEN}✓ On 'main' branch${NC}"

# Check remote
git -C "$PROJECT_ROOT" fetch origin main --quiet
LOCAL_SHA=$(git -C "$PROJECT_ROOT" rev-parse HEAD)
REMOTE_SHA=$(git -C "$PROJECT_ROOT" rev-parse origin/main)
if [[ "$LOCAL_SHA" != "$REMOTE_SHA" ]]; then
    echo -e "${YELLOW}⚠ Local main differs from origin/main${NC}"
    echo "  Local:  $LOCAL_SHA"
    echo "  Remote: $REMOTE_SHA"
fi

# Check for uncommitted changes
MODIFIED_COUNT=$(git -C "$PROJECT_ROOT" diff --name-only | wc -l | tr -d ' ')
UNTRACKED_COUNT=$(git -C "$PROJECT_ROOT" ls-files --others --exclude-standard | wc -l | tr -d ' ')
echo -e "${GREEN}✓ $MODIFIED_COUNT modified, $UNTRACKED_COUNT untracked files${NC}"

# ---------------------------------------------------------------------------
# Phase 2: Production readiness verification
# ---------------------------------------------------------------------------
echo ""
echo -e "${CYAN}Phase 2: Production Readiness${NC}"
echo -e "${CYAN}─────────────────────────────${NC}"

# Check critical files exist
CRITICAL_FILES=(
    "airaad/backend/Dockerfile"
    "airaad/backend/railway.toml"
    "airaad/frontend/vercel.json"
    "airaad/backend/config/settings/production.py"
    ".github/workflows/deploy-production.yml"
    ".github/workflows/ci.yml"
)

ALL_FILES_OK=true
for f in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$f" ]]; then
        echo -e "  ${GREEN}✓ $f${NC}"
    else
        echo -e "  ${RED}✗ MISSING: $f${NC}"
        ALL_FILES_OK=false
    fi
done

if [[ "$ALL_FILES_OK" == "false" ]]; then
    echo -e "${RED}✗ Critical files missing. Cannot deploy.${NC}"
    exit 1
fi

# Check production.py for DEBUG=False
if grep -q "^DEBUG = False" "$PROJECT_ROOT/airaad/backend/config/settings/production.py"; then
    echo -e "  ${GREEN}✓ DEBUG=False in production.py${NC}"
else
    echo -e "  ${RED}✗ DEBUG is NOT set to False in production.py — CRITICAL${NC}"
    exit 1
fi

# Check SECURE_SSL_REDIRECT
if grep -q "SECURE_SSL_REDIRECT" "$PROJECT_ROOT/airaad/backend/config/settings/production.py"; then
    echo -e "  ${GREEN}✓ SECURE_SSL_REDIRECT configured${NC}"
else
    echo -e "  ${RED}✗ SECURE_SSL_REDIRECT not found in production.py${NC}"
fi

# Check .dockerignore excludes .env
if grep -q "^\.env$" "$PROJECT_ROOT/airaad/backend/.dockerignore"; then
    echo -e "  ${GREEN}✓ .dockerignore excludes .env${NC}"
else
    echo -e "  ${RED}✗ .dockerignore does not exclude .env — SECURITY RISK${NC}"
fi

# Check no hardcoded secrets in Dockerfile
if grep -qi "SECRET_KEY\|PASSWORD\|API_KEY" "$PROJECT_ROOT/airaad/backend/Dockerfile" 2>/dev/null; then
    echo -e "  ${RED}✗ Possible hardcoded secret in Dockerfile${NC}"
    exit 1
else
    echo -e "  ${GREEN}✓ No secrets in Dockerfile${NC}"
fi

# Check vercel.json
VERCEL_FW=$(python3 -c "import json; print(json.load(open('$PROJECT_ROOT/airaad/frontend/vercel.json')).get('framework'))" 2>/dev/null)
VERCEL_OUT=$(python3 -c "import json; print(json.load(open('$PROJECT_ROOT/airaad/frontend/vercel.json')).get('outputDirectory'))" 2>/dev/null)
if [[ "$VERCEL_FW" == "None" && "$VERCEL_OUT" == "dist" ]]; then
    echo -e "  ${GREEN}✓ vercel.json: framework=null, output=dist${NC}"
else
    echo -e "  ${YELLOW}⚠ vercel.json may need review (framework=$VERCEL_FW, output=$VERCEL_OUT)${NC}"
fi

# ---------------------------------------------------------------------------
# Phase 3: GitHub secrets check
# ---------------------------------------------------------------------------
echo ""
echo -e "${CYAN}Phase 3: GitHub Secrets Check${NC}"
echo -e "${CYAN}─────────────────────────────${NC}"

if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
    SECRETS=$(gh secret list --repo "$REPO" 2>/dev/null || echo "")
    REQUIRED_SECRETS=(
        "RAILWAY_TOKEN"
        "RAILWAY_SERVICE_ID_BACKEND"
        "RAILWAY_PROD_URL"
        "VERCEL_TOKEN"
        "VERCEL_ORG_ID"
        "VERCEL_PROJECT_ID"
    )
    MISSING_SECRETS=0
    for SECRET in "${REQUIRED_SECRETS[@]}"; do
        if echo "$SECRETS" | grep -q "$SECRET"; then
            echo -e "  ${GREEN}✓ $SECRET${NC}"
        else
            echo -e "  ${RED}✗ MISSING: $SECRET${NC}"
            MISSING_SECRETS=$((MISSING_SECRETS + 1))
        fi
    done

    if [[ $MISSING_SECRETS -gt 0 ]]; then
        echo ""
        echo -e "${RED}✗ $MISSING_SECRETS required secret(s) missing.${NC}"
        echo -e "${YELLOW}Run ./scripts/setup-github-secrets.sh first.${NC}"
        read -p "Continue anyway? (y/n): " CONTINUE
        if [[ "$CONTINUE" != "y" ]]; then
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ GitHub CLI not available — cannot verify secrets.${NC}"
    echo "  Verify manually at: https://github.com/$REPO/settings/secrets/actions"
    echo ""
    echo "  Required secrets:"
    echo "    RAILWAY_TOKEN, RAILWAY_SERVICE_ID_BACKEND, RAILWAY_PROD_URL"
    echo "    VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID"
    echo ""
    read -p "Are all GitHub secrets configured? (y/n): " SECRETS_OK
    if [[ "$SECRETS_OK" != "y" ]]; then
        echo "Run ./scripts/setup-github-secrets.sh first."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Phase 4: Commit & push
# ---------------------------------------------------------------------------
echo ""
echo -e "${CYAN}Phase 4: Commit & Push${NC}"
echo -e "${CYAN}──────────────────────${NC}"

if [[ "$MODIFIED_COUNT" -gt 0 ]]; then
    echo ""
    echo "Modified files:"
    git -C "$PROJECT_ROOT" diff --name-only
    echo ""

    read -p "Stage and commit these changes? (y/n): " DO_COMMIT
    if [[ "$DO_COMMIT" == "y" ]]; then
        # Stage modified tracked files (not untracked playwright reports etc.)
        git -C "$PROJECT_ROOT" add -u
        echo ""
        read -p "Commit message [fix: E2E audit bug fixes — audit log date, dashboard health, total tags]: " COMMIT_MSG
        COMMIT_MSG=${COMMIT_MSG:-"fix: E2E audit bug fixes — audit log date, dashboard health, total tags"}
        git -C "$PROJECT_ROOT" commit -m "$COMMIT_MSG"
        echo -e "${GREEN}✓ Changes committed${NC}"
    fi
fi

echo ""
read -p "Push to origin/main? This will trigger CI → Production Deploy. (y/n): " DO_PUSH
if [[ "$DO_PUSH" == "y" ]]; then
    git -C "$PROJECT_ROOT" push origin main
    echo -e "${GREEN}✓ Pushed to origin/main${NC}"
    NEW_SHA=$(git -C "$PROJECT_ROOT" rev-parse --short HEAD)
    echo "  Commit: $NEW_SHA"
else
    echo -e "${YELLOW}⊘ Push cancelled. Run 'git push origin main' when ready.${NC}"
    exit 0
fi

# ---------------------------------------------------------------------------
# Phase 5: Monitor deployment
# ---------------------------------------------------------------------------
echo ""
echo -e "${CYAN}Phase 5: Monitor Deployment${NC}"
echo -e "${CYAN}───────────────────────────${NC}"
echo ""
echo "The push to main triggers this pipeline:"
echo ""
echo "  1. CI workflow runs (lint, test, build, security)"
echo "  2. On CI success → deploy-production.yml triggers:"
echo "     a. Creates git tag (rollback save point)"
echo "     b. Deploys backend to Railway"
echo "     c. Runs database migrations"
echo "     d. Deploys frontend to Vercel"
echo "     e. Post-deploy verification (health, DEBUG, auth, HTTPS)"
echo "     f. Auto-rollback if verification fails"
echo "     g. Team notification"
echo ""

if command -v gh &>/dev/null; then
    echo -e "${YELLOW}Monitoring CI workflow...${NC}"
    echo ""
    echo "Watch live at:"
    echo "  https://github.com/$REPO/actions"
    echo ""
    read -p "Open GitHub Actions in browser? (y/n): " OPEN_BROWSER
    if [[ "$OPEN_BROWSER" == "y" ]]; then
        open "https://github.com/$REPO/actions" 2>/dev/null || \
            xdg-open "https://github.com/$REPO/actions" 2>/dev/null || \
            echo "  Open manually: https://github.com/$REPO/actions"
    fi

    echo ""
    echo -e "${YELLOW}Waiting for CI to start (up to 30s)...${NC}"
    sleep 10

    # Try to get the latest workflow run
    RUN_URL=$(gh run list --repo "$REPO" --branch main --limit 1 --json url --jq '.[0].url' 2>/dev/null || echo "")
    if [[ -n "$RUN_URL" ]]; then
        echo -e "  Latest run: ${CYAN}$RUN_URL${NC}"
        echo ""
        read -p "Watch CI run in terminal? (y/n): " WATCH_CI
        if [[ "$WATCH_CI" == "y" ]]; then
            RUN_ID=$(gh run list --repo "$REPO" --branch main --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null)
            gh run watch "$RUN_ID" --repo "$REPO" --exit-status || true
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Production Deploy Initiated!${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""
echo "Monitor at: https://github.com/$REPO/actions"
echo ""
echo "Post-deploy verification URLs:"
echo "  Backend health: curl <RAILWAY_PROD_URL>/api/v1/health/"
echo "  Frontend:       open <VERCEL_PROD_URL>"
echo ""
echo "Rollback (if needed):"
echo "  Backend:  railway rollback --service backend"
echo "  Frontend: vercel promote <previous-deployment-url>"
echo ""
