# AirAd AI Code Review — Implementation Playbook

This document describes every tool, config file, and workflow step that makes up
the AI-powered code review pipeline for the AirAd project.

---

## Architecture Overview

```
Pull Request opened / updated
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  GitHub Actions CI  (.github/workflows/ci.yml)        │
│                                                       │
│  Job 7: semgrep          ──► semgrep-merged.json      │
│  Job 8: secret-scan      ──► TruffleHog (blocks PR)   │
│  Job 9: ai-review        ──► Claude API               │
│                               + semgrep-merged.json   │
│                               ──► review-comments.json│
│                               ──► GitHub PR comments  │
│  Job 10: quality-gate    ──► exits 1 on CRITICAL      │
└───────────────────────────────────────────────────────┘
```

---

## Files Created

| File | Purpose |
|------|---------|
| `airaad/.semgrep.yml` | Project-specific Semgrep rules (Django, DRF, React, TS) |
| `airaad/.trufflehog.yml` | TruffleHog v3 config (detectors, exclusions) |
| `airaad/scripts/ai_review.py` | Claude + Semgrep orchestrator script |
| `.github/workflows/ci.yml` | Extended with Jobs 7–10 |
| `skills/code-review-ai-ai-review/resources/implementation-playbook.md` | This file |

---

## GitHub Secrets Required

Add these in **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Value | Required for |
|--------|-------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Job 9 (AI review) |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions | Job 9 (posting comments) |

> `GITHUB_TOKEN` is automatically available in every Actions run — you do **not**
> need to create it manually.

---

## Tool Details

### Semgrep (Job 7)

**What it does:** Static analysis across Python (Django/DRF) and TypeScript (React).

**Two scan passes:**
1. **Project rules** (`airaad/.semgrep.yml`) — AirAd-specific patterns:
   - Raw SQL injection in Django ORM
   - `DEBUG=True` / `SECRET_KEY` hardcoded in settings
   - `AllowAny` on non-auth views
   - Missing throttle on token views
   - N+1 query patterns in loops
   - `dangerouslySetInnerHTML` in React
   - `localStorage` storing JWT/password
   - Hardcoded secrets in TypeScript

2. **Community rulesets** (`p/django`, `p/python`, `p/react`, `p/typescript`, `p/owasp-top-ten`) —
   Semgrep's maintained rule packs covering 500+ patterns.

**Output:** `semgrep-merged.json` (uploaded as Actions artifact, passed to Job 9).

**Local run:**
```bash
# Install
pip install semgrep

# Run project rules only
semgrep scan --config airaad/.semgrep.yml airaad/

# Run with community rulesets
semgrep scan --config p/django --config p/owasp-top-ten airaad/

# Output JSON for ai_review.py
semgrep scan --config airaad/.semgrep.yml --json --output semgrep.json airaad/
```

---

### TruffleHog (Job 8)

**What it does:** Scans git history for leaked secrets (AWS keys, API tokens,
private keys, DB connection strings with passwords).

**Config:** `airaad/.trufflehog.yml`
- Enabled detectors: AWS, GitHub, Anthropic, OpenAI, Stripe, Slack, SendGrid, Twilio, Postgres, PrivateKey, URI
- Excluded: `.venv/`, `node_modules/`, test fixtures, build artifacts
- Scans only the commits introduced by the PR (base → head), not the full history

**Behaviour:** Fails the job (`--fail`) if any verified secret is found, blocking the merge.

**Local run:**
```bash
# Install
brew install trufflehog
# or
docker run --rm -v "$PWD:/pwd" trufflesecurity/trufflehog:latest git file:///pwd

# Scan local repo
trufflehog git file://. --config airaad/.trufflehog.yml --json

# Scan only recent commits
trufflehog git file://. --since-commit HEAD~5 --json
```

---

### AI Review Script (Job 9)

**File:** `airaad/scripts/ai_review.py`

**What it does:**
1. Parses `semgrep-merged.json` into structured `ReviewIssue` objects
2. Fetches the PR diff from GitHub API (capped at 20 000 chars)
3. Sends diff + Semgrep summary to **Claude 3.5 Sonnet** with an AirAd-specific
   prompt focusing on issues static analysis cannot catch:
   - Business logic bugs, IDOR, missing permission checks
   - Django ORM N+1 / unbounded querysets
   - React stale closures, missing `useEffect` deps
   - TypeScript unsafe casts, missing null checks
   - Celery task reliability (missing retry, non-idempotent)
4. Parses Claude's JSON response into additional `ReviewIssue` objects
5. Posts a PR review to GitHub with inline comments (severity-coloured)
6. Writes `review-comments.json` for the quality gate
7. Exits with code 1 if any CRITICAL issue is found

**CLI flags:**
```
--pr-number   GitHub PR number (required)
--repo        owner/repo format (required)
--semgrep-results  path to semgrep JSON (default: semgrep.json)
--output      path for combined output (default: review-comments.json)
--dry-run     print findings without posting to GitHub
--skip-ai     Semgrep findings only, no Claude call
```

**Local dry-run:**
```bash
# Install deps
pip install anthropic requests

# Run against a real PR (no GitHub posting)
ANTHROPIC_API_KEY=sk-ant-... \
python airaad/scripts/ai_review.py \
  --pr-number 42 \
  --repo yourorg/airaad \
  --semgrep-results semgrep.json \
  --dry-run

# Semgrep-only (no API key needed)
python airaad/scripts/ai_review.py \
  --pr-number 42 \
  --repo yourorg/airaad \
  --semgrep-results semgrep.json \
  --skip-ai \
  --dry-run
```

---

### Quality Gate (Job 10)

**What it does:** Reads `review-comments.json` and exits 1 if any `CRITICAL`
severity issue is present, preventing the PR from being merged.

**Severity policy:**
| Severity | Gate behaviour |
|----------|---------------|
| CRITICAL | ❌ Blocks merge |
| HIGH | ⚠️ Warning only (logged, does not block) |
| MEDIUM / LOW / INFO | ✅ Informational |

---

## Tuning the Rules

### Adding a new Semgrep rule

Edit `airaad/.semgrep.yml` and add a new entry under `rules:`. Test locally:
```bash
semgrep scan --config airaad/.semgrep.yml --test airaad/
```

### Suppressing a false positive

Add an inline comment to the offending line:
```python
result = queryset.extra(where=[dynamic_expr])  # nosemgrep: django-extra-sql-injection
```

Or add a path exclusion in `.semgrep.yml`:
```yaml
paths:
  exclude:
    - airaad/backend/apps/legacy/**
```

### Adjusting the quality gate threshold

To also block on HIGH findings, edit the quality gate step in `ci.yml`:
```python
if critical or high:   # change from: if critical:
```

---

## Extending to SonarQube / CodeQL

These tools were listed in the skill but are **not set up** because they require
external service accounts. When ready:

- **SonarQube Cloud**: Add `SONAR_TOKEN` secret, use `sonarsource/sonarcloud-github-action@master`
- **CodeQL**: Use `github/codeql-action/analyze@v3` — free for public repos,
  requires GitHub Advanced Security for private repos

Both can feed their SARIF output into the existing `ai_review.py` by extending
the `parse_semgrep_results` function to also parse SARIF format.
