#!/usr/bin/env bash
# =============================================================================
# AirAd — Vercel Production Setup
# =============================================================================
# Creates the Vercel production project for the frontend.
# Run this ONCE after Railway setup is complete.
#
# Prerequisites:
#   - Vercel CLI installed: npm i -g vercel
#   - Logged in: vercel login
#   - Railway backend URL known
#
# Usage:
#   chmod +x scripts/setup-vercel-prod.sh
#   ./scripts/setup-vercel-prod.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/airaad/frontend"

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AirAd — Vercel Production Setup${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""

if ! command -v vercel &>/dev/null; then
    echo -e "${RED}✗ Vercel CLI not found. Install with: npm i -g vercel${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Vercel CLI found${NC}"

# Check if we have Railway secrets from previous step
SECRETS_FILE="$PROJECT_ROOT/.railway-prod-secrets.tmp"
if [[ -f "$SECRETS_FILE" ]]; then
    source "$SECRETS_FILE"
    echo -e "${GREEN}✓ Loaded Railway secrets from previous step${NC}"
    echo "  Backend URL: ${RAILWAY_PROD_URL:-not set}"
fi

# ---------------------------------------------------------------------------
# Get backend URL
# ---------------------------------------------------------------------------
echo ""
if [[ -z "${RAILWAY_PROD_URL:-}" ]]; then
    echo -e "${YELLOW}Enter the Railway production backend URL:${NC}"
    read -p "Backend URL (e.g., https://airaad-backend.up.railway.app): " RAILWAY_PROD_URL
fi

# ---------------------------------------------------------------------------
# Link or create Vercel project
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Setting up Vercel project ──${NC}"
echo ""
echo "Options:"
echo "  1. Link to existing Vercel project"
echo "  2. Create new Vercel project"
echo ""
read -p "Choose (1 or 2): " VERCEL_CHOICE

if [[ "$VERCEL_CHOICE" == "2" ]]; then
    echo ""
    echo -e "${YELLOW}Creating Vercel project...${NC}"
    echo "When prompted:"
    echo "  - Set up and deploy? → N (we'll deploy via CI)"
    echo "  - Which scope? → Select your org"
    echo "  - Link to existing project? → N"
    echo "  - Project name? → airaad (or your preferred name)"
    echo "  - Root directory? → ./ (we're already in airaad/frontend)"
    echo ""
    (cd "$FRONTEND_DIR" && vercel link)
else
    echo ""
    echo -e "${YELLOW}Linking to existing Vercel project...${NC}"
    (cd "$FRONTEND_DIR" && vercel link)
fi

# ---------------------------------------------------------------------------
# Extract Vercel IDs
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Extracting Vercel project IDs ──${NC}"

VERCEL_PROJECT_JSON="$FRONTEND_DIR/.vercel/project.json"
if [[ -f "$VERCEL_PROJECT_JSON" ]]; then
    VERCEL_ORG_ID=$(python3 -c "import json; print(json.load(open('$VERCEL_PROJECT_JSON'))['orgId'])")
    VERCEL_PROJECT_ID=$(python3 -c "import json; print(json.load(open('$VERCEL_PROJECT_JSON'))['projectId'])")
    echo -e "${GREEN}✓ Vercel Org ID: ${VERCEL_ORG_ID}${NC}"
    echo -e "${GREEN}✓ Vercel Project ID: ${VERCEL_PROJECT_ID}${NC}"
else
    echo -e "${YELLOW}Could not find .vercel/project.json. Enter IDs manually:${NC}"
    read -p "Vercel Org ID: " VERCEL_ORG_ID
    read -p "Vercel Project ID: " VERCEL_PROJECT_ID
fi

# ---------------------------------------------------------------------------
# Set Vercel environment variables
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Setting Vercel environment variables ──${NC}"

echo "Setting VITE_API_BASE_URL for production..."
(cd "$FRONTEND_DIR" && echo "$RAILWAY_PROD_URL" | vercel env add VITE_API_BASE_URL production) 2>/dev/null || {
    echo -e "${YELLOW}⚠ Variable may already exist. Remove and re-add if needed:${NC}"
    echo "  vercel env rm VITE_API_BASE_URL production"
    echo "  echo '$RAILWAY_PROD_URL' | vercel env add VITE_API_BASE_URL production"
}

echo "Setting VITE_APP_ENV for production..."
(cd "$FRONTEND_DIR" && echo "production" | vercel env add VITE_APP_ENV production) 2>/dev/null || {
    echo -e "${YELLOW}⚠ Variable may already exist.${NC}"
}

echo -e "${GREEN}✓ Vercel environment variables set${NC}"

# ---------------------------------------------------------------------------
# Verify vercel.json
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Verifying vercel.json ──${NC}"

if [[ -f "$FRONTEND_DIR/vercel.json" ]]; then
    # Check required fields
    FRAMEWORK=$(python3 -c "import json; d=json.load(open('$FRONTEND_DIR/vercel.json')); print(d.get('framework', 'MISSING'))")
    OUTPUT=$(python3 -c "import json; d=json.load(open('$FRONTEND_DIR/vercel.json')); print(d.get('outputDirectory', 'MISSING'))")
    HAS_REWRITE=$(python3 -c "import json; d=json.load(open('$FRONTEND_DIR/vercel.json')); print('yes' if d.get('rewrites') else 'no')")

    if [[ "$FRAMEWORK" == "None" ]]; then
        echo -e "${GREEN}✓ framework: null (correct for Vite)${NC}"
    else
        echo -e "${RED}✗ framework should be null, got: $FRAMEWORK${NC}"
    fi

    if [[ "$OUTPUT" == "dist" ]]; then
        echo -e "${GREEN}✓ outputDirectory: dist${NC}"
    else
        echo -e "${RED}✗ outputDirectory should be 'dist', got: $OUTPUT${NC}"
    fi

    if [[ "$HAS_REWRITE" == "yes" ]]; then
        echo -e "${GREEN}✓ SPA rewrites configured${NC}"
    else
        echo -e "${RED}✗ Missing SPA rewrite rule${NC}"
    fi
else
    echo -e "${RED}✗ vercel.json not found at $FRONTEND_DIR/vercel.json${NC}"
    exit 1
fi

# ---------------------------------------------------------------------------
# Get Vercel token
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Vercel API Token ──${NC}"
echo -e "${YELLOW}Generate a token for GitHub Actions:${NC}"
echo "  Vercel Dashboard → Settings → Tokens → Create"
echo "  Name: 'github-actions'"
echo "  Scope: Full Account"
echo ""
read -p "Enter Vercel Token: " VERCEL_TOKEN

# ---------------------------------------------------------------------------
# Get Vercel production URL
# ---------------------------------------------------------------------------
echo ""
echo -e "${YELLOW}What will the production frontend URL be?${NC}"
echo "  (e.g., https://airaad.vercel.app or a custom domain)"
read -p "Frontend Production URL: " VERCEL_PROD_URL_FINAL

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Vercel Production Setup Complete!${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""
echo "Save these values for GitHub Secrets setup:"
echo ""
echo -e "${YELLOW}  VERCEL_TOKEN=${NC}${VERCEL_TOKEN}"
echo -e "${YELLOW}  VERCEL_ORG_ID=${NC}${VERCEL_ORG_ID}"
echo -e "${YELLOW}  VERCEL_PROJECT_ID=${NC}${VERCEL_PROJECT_ID}"
echo -e "${YELLOW}  VERCEL_PROD_URL=${NC}${VERCEL_PROD_URL_FINAL}"
echo ""

# Save/append to secrets file
SECRETS_FILE="$PROJECT_ROOT/.railway-prod-secrets.tmp"
cat >> "$SECRETS_FILE" <<EOF
VERCEL_TOKEN=$VERCEL_TOKEN
VERCEL_ORG_ID=$VERCEL_ORG_ID
VERCEL_PROJECT_ID=$VERCEL_PROJECT_ID
VERCEL_PROD_URL=$VERCEL_PROD_URL_FINAL
EOF
echo -e "${GREEN}✓ Secrets appended to .railway-prod-secrets.tmp${NC}"
echo ""
echo "Next step: Run ./scripts/setup-github-secrets.sh"
