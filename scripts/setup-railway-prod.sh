#!/usr/bin/env bash
# =============================================================================
# AirAd — Railway Production Setup
# =============================================================================
# Creates the Railway production project with all required services and
# environment variables. Run this ONCE for initial production setup.
#
# Prerequisites:
#   - Railway CLI installed: npm i -g @railway/cli
#   - Railway account with billing enabled
#   - Logged in: railway login
#
# Usage:
#   chmod +x scripts/setup-railway-prod.sh
#   ./scripts/setup-railway-prod.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AirAd — Railway Production Setup${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""

if ! command -v railway &>/dev/null; then
    echo -e "${RED}✗ Railway CLI not found. Install with: npm i -g @railway/cli${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Railway CLI found${NC}"

if ! railway whoami &>/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Not logged in to Railway. Running 'railway login'...${NC}"
    railway login
fi
echo -e "${GREEN}✓ Logged in to Railway${NC}"

# ---------------------------------------------------------------------------
# Generate secrets
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Generating production secrets ──${NC}"

DJANGO_SECRET_KEY=$(python3 -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
print(''.join(secrets.choice(chars) for _ in range(64)))
")
echo -e "${GREEN}✓ Django SECRET_KEY generated (64 chars)${NC}"

ENCRYPTION_KEY=$(python3 -c "
import os, base64
print(base64.b64encode(os.urandom(32)).decode())
")
echo -e "${GREEN}✓ ENCRYPTION_KEY generated (32 bytes, base64)${NC}"

# ---------------------------------------------------------------------------
# Create Railway project
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Creating Railway project: airaad-prod ──${NC}"
echo -e "${YELLOW}NOTE: If the project already exists, Railway will error. That's OK — just link to it instead.${NC}"
echo ""

read -p "Create new project 'airaad-prod'? (y/n): " CREATE_PROJECT
if [[ "$CREATE_PROJECT" == "y" ]]; then
    railway init --name airaad-prod || echo -e "${YELLOW}⚠ Project may already exist. Linking instead...${NC}"
fi

echo ""
echo -e "${YELLOW}Link to the airaad-prod project (select it from the list):${NC}"
railway link

# ---------------------------------------------------------------------------
# Add PostgreSQL + Redis plugins
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Adding database plugins ──${NC}"
echo -e "${YELLOW}You need to add PostgreSQL and Redis via the Railway Dashboard:${NC}"
echo ""
echo "  1. Go to https://railway.app → airaad-prod project"
echo "  2. Click '+ New' → 'Database' → 'PostgreSQL'"
echo "  3. Click '+ New' → 'Database' → 'Redis'"
echo ""
echo -e "${YELLOW}After adding both plugins, enable PostGIS:${NC}"
echo "  - Click on PostgreSQL service → 'Data' tab → 'Query'"
echo "  - Run: CREATE EXTENSION IF NOT EXISTS postgis;"
echo "  - Run: CREATE EXTENSION IF NOT EXISTS postgis_topology;"
echo ""
read -p "Press Enter once PostgreSQL + Redis are provisioned and PostGIS is enabled..."

# ---------------------------------------------------------------------------
# Create backend service
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Creating backend service ──${NC}"
echo -e "${YELLOW}Create the backend service via Railway Dashboard:${NC}"
echo ""
echo "  1. Click '+ New' → 'Service' → 'Connect GitHub Repo'"
echo "     Select: iexpertapps/AirAds-web"
echo "  2. Settings:"
echo "     - Service name: backend"
echo "     - Root Directory: airaad/backend"
echo "     - Watch Paths: airaad/backend/**"
echo ""
read -p "Press Enter once the backend service is created..."

echo ""
echo -e "${YELLOW}Enter the backend service ID (from Railway Dashboard URL or 'railway service list'):${NC}"
read -p "Backend Service ID: " RAILWAY_SERVICE_ID_BACKEND

# ---------------------------------------------------------------------------
# Set backend environment variables
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Setting backend environment variables ──${NC}"

echo -e "${YELLOW}Enter the Railway backend URL (e.g., https://airaad-backend.up.railway.app):${NC}"
read -p "Backend URL: " RAILWAY_PROD_URL

echo -e "${YELLOW}Enter the Vercel production frontend URL (e.g., https://airaad.vercel.app):${NC}"
read -p "Frontend URL: " VERCEL_PROD_URL

echo ""
echo "Setting environment variables on Railway backend service..."

railway variables set \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    "SECRET_KEY=$DJANGO_SECRET_KEY" \
    "ENCRYPTION_KEY=$ENCRYPTION_KEY" \
    DEBUG=False \
    "ALLOWED_HOSTS=${RAILWAY_PROD_URL#https://}" \
    "CORS_ALLOWED_ORIGINS=$VERCEL_PROD_URL" \
    "FRONTEND_URL=$VERCEL_PROD_URL" \
    SECURE_SSL_REDIRECT=True \
    NUM_PROXIES=1 \
    --service "$RAILWAY_SERVICE_ID_BACKEND" 2>/dev/null || {
        echo -e "${YELLOW}⚠ Bulk set failed. Setting variables one by one...${NC}"
        railway variables set "DJANGO_SETTINGS_MODULE=config.settings.production" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "SECRET_KEY=$DJANGO_SECRET_KEY" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "ENCRYPTION_KEY=$ENCRYPTION_KEY" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "DEBUG=False" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "ALLOWED_HOSTS=${RAILWAY_PROD_URL#https://}" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "CORS_ALLOWED_ORIGINS=$VERCEL_PROD_URL" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "FRONTEND_URL=$VERCEL_PROD_URL" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "SECURE_SSL_REDIRECT=True" --service "$RAILWAY_SERVICE_ID_BACKEND"
        railway variables set "NUM_PROXIES=1" --service "$RAILWAY_SERVICE_ID_BACKEND"
    }

echo -e "${GREEN}✓ Backend environment variables set${NC}"

echo ""
echo -e "${YELLOW}AWS S3 (for media/static storage). Leave blank to skip:${NC}"
read -p "AWS_ACCESS_KEY_ID: " AWS_KEY
if [[ -n "$AWS_KEY" ]]; then
    read -p "AWS_SECRET_ACCESS_KEY: " AWS_SECRET
    read -p "AWS_STORAGE_BUCKET_NAME [airaad-prod]: " AWS_BUCKET
    AWS_BUCKET=${AWS_BUCKET:-airaad-prod}
    read -p "AWS_S3_REGION_NAME [us-east-1]: " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}

    railway variables set "AWS_ACCESS_KEY_ID=$AWS_KEY" --service "$RAILWAY_SERVICE_ID_BACKEND"
    railway variables set "AWS_SECRET_ACCESS_KEY=$AWS_SECRET" --service "$RAILWAY_SERVICE_ID_BACKEND"
    railway variables set "AWS_STORAGE_BUCKET_NAME=$AWS_BUCKET" --service "$RAILWAY_SERVICE_ID_BACKEND"
    railway variables set "AWS_S3_REGION_NAME=$AWS_REGION" --service "$RAILWAY_SERVICE_ID_BACKEND"
    echo -e "${GREEN}✓ AWS S3 variables set${NC}"
fi

echo ""
echo -e "${YELLOW}Google Places API Key (leave blank to skip):${NC}"
read -p "GOOGLE_PLACES_API_KEY: " GPLACES_KEY
if [[ -n "$GPLACES_KEY" ]]; then
    railway variables set "GOOGLE_PLACES_API_KEY=$GPLACES_KEY" --service "$RAILWAY_SERVICE_ID_BACKEND"
    echo -e "${GREEN}✓ Google Places API key set${NC}"
fi

# ---------------------------------------------------------------------------
# Link DATABASE_URL and REDIS_URL from plugins
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Link DATABASE_URL and REDIS_URL ──${NC}"
echo -e "${YELLOW}Railway auto-injects these from plugins. Verify they appear:${NC}"
echo "  railway variables list --service $RAILWAY_SERVICE_ID_BACKEND"
echo ""
echo -e "${YELLOW}If DATABASE_URL or REDIS_URL are missing, set them manually:${NC}"
echo '  Railway Dashboard → backend service → Variables → Add Reference Variable'
echo '  DATABASE_URL → ${{Postgres.DATABASE_URL}}'
echo '  REDIS_URL → ${{Redis.REDIS_URL}}'
echo '  CELERY_BROKER_URL → ${{Redis.REDIS_URL}}'
echo '  CELERY_RESULT_BACKEND → ${{Redis.REDIS_URL}}'
echo ""
read -p "Press Enter once DATABASE_URL and REDIS_URL are confirmed..."

# ---------------------------------------------------------------------------
# Create Celery worker service
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Creating Celery worker service ──${NC}"
echo -e "${YELLOW}Create a second service via Railway Dashboard:${NC}"
echo ""
echo "  1. Click '+ New' → 'Service' → 'Connect GitHub Repo'"
echo "     Select: iexpertapps/AirAds-web"
echo "  2. Settings:"
echo "     - Service name: celery"
echo "     - Root Directory: airaad/backend"
echo "     - Watch Paths: airaad/backend/**"
echo "     - Start Command: celery -A config worker --loglevel=info --concurrency=2"
echo ""
echo "  3. Copy ALL environment variables from backend service to celery service"
echo "     (Railway Dashboard → celery → Variables → 'Raw Editor' → paste)"
echo ""
read -p "Press Enter once Celery service is created..."

echo -e "${YELLOW}Enter the Celery service ID:${NC}"
read -p "Celery Service ID: " RAILWAY_SERVICE_ID_CELERY

# ---------------------------------------------------------------------------
# Generate Railway API token
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}── Railway API Token ──${NC}"
echo -e "${YELLOW}Generate a project-scoped API token for GitHub Actions:${NC}"
echo "  Railway Dashboard → Account Settings → Tokens → Create Token"
echo "  Name: 'github-actions-prod'"
echo "  Scope: Project (airaad-prod)"
echo ""
read -p "Enter the Railway API Token: " RAILWAY_TOKEN

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Railway Production Setup Complete!${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo ""
echo "Save these values for GitHub Secrets setup:"
echo ""
echo -e "${YELLOW}  RAILWAY_TOKEN=${NC}${RAILWAY_TOKEN}"
echo -e "${YELLOW}  RAILWAY_SERVICE_ID_BACKEND=${NC}${RAILWAY_SERVICE_ID_BACKEND}"
echo -e "${YELLOW}  RAILWAY_SERVICE_ID_CELERY=${NC}${RAILWAY_SERVICE_ID_CELERY}"
echo -e "${YELLOW}  RAILWAY_PROD_URL=${NC}${RAILWAY_PROD_URL}"
echo ""

# Save to temp file for the GitHub secrets script
SECRETS_FILE="$PROJECT_ROOT/.railway-prod-secrets.tmp"
cat > "$SECRETS_FILE" <<EOF
RAILWAY_TOKEN=$RAILWAY_TOKEN
RAILWAY_SERVICE_ID_BACKEND=$RAILWAY_SERVICE_ID_BACKEND
RAILWAY_SERVICE_ID_CELERY=$RAILWAY_SERVICE_ID_CELERY
RAILWAY_PROD_URL=$RAILWAY_PROD_URL
VERCEL_PROD_URL=$VERCEL_PROD_URL
EOF
echo -e "${GREEN}✓ Secrets saved to .railway-prod-secrets.tmp (gitignored, delete after use)${NC}"
echo ""
echo "Next step: Run ./scripts/setup-vercel-prod.sh"
