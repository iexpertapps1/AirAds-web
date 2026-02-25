#!/usr/bin/env bash
# =============================================================================
# AirAd — GitHub Secrets Setup for Production
# =============================================================================
# Configures all required GitHub Actions secrets for the production deploy
# workflow. Run this AFTER Railway and Vercel setup scripts.
#
# Prerequisites:
#   - GitHub CLI installed: brew install gh
#   - Authenticated: gh auth login
#   - .railway-prod-secrets.tmp exists (from previous scripts)
#     OR you can enter values manually
#
# Usage:
#   chmod +x scripts/setup-github-secrets.sh
#   ./scripts/setup-github-secrets.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO="iexpertapps/AirAds-web"

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AirAd — GitHub Secrets Setup (Production)${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""

if ! command -v gh &>/dev/null; then
    echo -e "${RED}✗ GitHub CLI not found. Install with: brew install gh${NC}"
    echo ""
    echo "Alternative: Set secrets manually at:"
    echo "  https://github.com/$REPO/settings/secrets/actions"
    echo ""
    echo "Required secrets:"
    echo "  RAILWAY_TOKEN"
    echo "  RAILWAY_SERVICE_ID_BACKEND"
    echo "  RAILWAY_SERVICE_ID_CELERY (optional — only if celery service exists)"
    echo "  RAILWAY_PROD_URL"
    echo "  VERCEL_TOKEN"
    echo "  VERCEL_ORG_ID"
    echo "  VERCEL_PROJECT_ID"
    echo "  SLACK_WEBHOOK_URL (optional)"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI found${NC}"

if ! gh auth status &>/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Not authenticated. Running 'gh auth login'...${NC}"
    gh auth login
fi
echo -e "${GREEN}✓ Authenticated with GitHub${NC}"

# ---------------------------------------------------------------------------
# Load saved secrets or prompt
# ---------------------------------------------------------------------------
SECRETS_FILE="$PROJECT_ROOT/.railway-prod-secrets.tmp"

prompt_or_load() {
    local VAR_NAME="$1"
    local PROMPT="$2"
    local CURRENT_VAL="${!VAR_NAME:-}"

    if [[ -n "$CURRENT_VAL" ]]; then
        echo -e "  ${GREEN}✓ $VAR_NAME${NC} (loaded from previous step)"
        read -p "    Use '$CURRENT_VAL'? (Enter=yes, or type new value): " NEW_VAL
        if [[ -n "$NEW_VAL" ]]; then
            eval "$VAR_NAME='$NEW_VAL'"
        fi
    else
        read -p "  $PROMPT: " "$VAR_NAME"
    fi
}

echo ""
if [[ -f "$SECRETS_FILE" ]]; then
    echo -e "${GREEN}✓ Loading saved values from .railway-prod-secrets.tmp${NC}"
    source "$SECRETS_FILE"
else
    echo -e "${YELLOW}No saved secrets file found. You'll enter values manually.${NC}"
fi

echo ""
echo -e "${BLUE}── Railway Secrets ──${NC}"
prompt_or_load "RAILWAY_TOKEN" "RAILWAY_TOKEN (API token)"
prompt_or_load "RAILWAY_SERVICE_ID_BACKEND" "RAILWAY_SERVICE_ID_BACKEND"
prompt_or_load "RAILWAY_PROD_URL" "RAILWAY_PROD_URL (e.g., https://airaad-backend.up.railway.app)"

echo ""
echo -e "${YELLOW}Celery service ID (leave blank if not yet created):${NC}"
prompt_or_load "RAILWAY_SERVICE_ID_CELERY" "RAILWAY_SERVICE_ID_CELERY"

echo ""
echo -e "${BLUE}── Vercel Secrets ──${NC}"
prompt_or_load "VERCEL_TOKEN" "VERCEL_TOKEN (API token)"
prompt_or_load "VERCEL_ORG_ID" "VERCEL_ORG_ID"
prompt_or_load "VERCEL_PROJECT_ID" "VERCEL_PROJECT_ID"

echo ""
echo -e "${BLUE}── Optional Secrets ──${NC}"
echo -e "${YELLOW}Slack webhook URL for deploy notifications (leave blank to skip):${NC}"
read -p "  SLACK_WEBHOOK_URL: " SLACK_WEBHOOK_URL

# ---------------------------------------------------------------------------
# Set GitHub secrets
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Setting GitHub Secrets on $REPO ──${NC}"
echo ""

set_secret() {
    local NAME="$1"
    local VALUE="$2"
    if [[ -z "$VALUE" ]]; then
        echo -e "  ${YELLOW}⊘ Skipping $NAME (empty)${NC}"
        return
    fi
    echo "$VALUE" | gh secret set "$NAME" --repo "$REPO" 2>/dev/null && \
        echo -e "  ${GREEN}✓ $NAME${NC}" || \
        echo -e "  ${RED}✗ Failed to set $NAME${NC}"
}

set_secret "RAILWAY_TOKEN" "${RAILWAY_TOKEN:-}"
set_secret "RAILWAY_SERVICE_ID_BACKEND" "${RAILWAY_SERVICE_ID_BACKEND:-}"
set_secret "RAILWAY_SERVICE_ID_CELERY" "${RAILWAY_SERVICE_ID_CELERY:-}"
set_secret "RAILWAY_PROD_URL" "${RAILWAY_PROD_URL:-}"
set_secret "VERCEL_TOKEN" "${VERCEL_TOKEN:-}"
set_secret "VERCEL_ORG_ID" "${VERCEL_ORG_ID:-}"
set_secret "VERCEL_PROJECT_ID" "${VERCEL_PROJECT_ID:-}"
set_secret "SLACK_WEBHOOK_URL" "${SLACK_WEBHOOK_URL:-}"

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Verifying secrets ──${NC}"
echo ""
gh secret list --repo "$REPO" 2>/dev/null || echo -e "${YELLOW}Could not list secrets (may need admin access)${NC}"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  GitHub Secrets Setup Complete!${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""
echo "Secrets configured for: $REPO"
echo ""
echo -e "${YELLOW}IMPORTANT: The deploy-production.yml workflow also uses${NC}"
echo -e "${YELLOW}GitHub Environment secrets. Make sure the 'production'${NC}"
echo -e "${YELLOW}environment exists:${NC}"
echo "  https://github.com/$REPO/settings/environments"
echo ""

# ---------------------------------------------------------------------------
# Cleanup temp secrets file
# ---------------------------------------------------------------------------
if [[ -f "$SECRETS_FILE" ]]; then
    read -p "Delete .railway-prod-secrets.tmp? (y/n): " DELETE_SECRETS
    if [[ "$DELETE_SECRETS" == "y" ]]; then
        rm -f "$SECRETS_FILE"
        echo -e "${GREEN}✓ Temp secrets file deleted${NC}"
    else
        echo -e "${YELLOW}⚠ Remember to delete .railway-prod-secrets.tmp manually!${NC}"
    fi
fi

echo ""
echo "Next step: Run ./scripts/deploy-production.sh"
