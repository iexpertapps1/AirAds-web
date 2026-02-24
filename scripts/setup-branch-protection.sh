#!/usr/bin/env bash
# =============================================================================
# AirAd — GitHub Branch Protection Setup
# =============================================================================
# Requires: GitHub CLI (gh) authenticated with admin access
# Usage: bash scripts/setup-branch-protection.sh
# =============================================================================

set -euo pipefail

REPO="iexpertapps/AirAds-web"

echo "=== Setting up branch protection rules for $REPO ==="
echo ""

# -------------------------------------------------------------------------
# main — Production (strictest)
# -------------------------------------------------------------------------
echo "Configuring protection for 'main' (production)..."
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Test Suite", "Frontend Build", "Backend Docker Build"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
echo "✅ main branch protection configured"
echo ""

# -------------------------------------------------------------------------
# staging — Pre-production
# -------------------------------------------------------------------------
echo "Configuring protection for 'staging'..."
gh api repos/$REPO/branches/staging/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["Test Suite", "Frontend Build"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
echo "✅ staging branch protection configured"
echo ""

# -------------------------------------------------------------------------
# develop — Active development
# -------------------------------------------------------------------------
echo "Configuring protection for 'develop'..."
gh api repos/$REPO/branches/develop/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["Test Suite", "Frontend Build"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
echo "✅ develop branch protection configured"
echo ""

echo "=== All branch protection rules configured ==="
echo ""
echo "Summary:"
echo "  main    → PR required (1 approval), CI must pass, no force push"
echo "  staging → PR required (1 approval), CI must pass, no force push"
echo "  develop → CI must pass, no force push"
