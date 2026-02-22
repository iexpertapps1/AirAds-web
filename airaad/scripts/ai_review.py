#!/usr/bin/env python3
"""
AirAd AI Code Review Script
============================
Orchestrates Semgrep static analysis + Claude AI review for pull requests.

Usage (GitHub Actions):
    python scripts/ai_review.py \
        --pr-number 42 \
        --repo owner/airaad \
        --semgrep-results semgrep.json

Usage (local dry-run, no GitHub posting):
    python scripts/ai_review.py \
        --pr-number 42 \
        --repo owner/airaad \
        --semgrep-results semgrep.json \
        --dry-run

Required environment variables:
    ANTHROPIC_API_KEY   — Claude API key
    GITHUB_TOKEN        — GitHub personal access token (for posting comments)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from dataclasses import asdict, dataclass, field
from typing import Any

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic>=0.25.0")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests package not installed. Run: pip install requests>=2.31.0")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ReviewIssue:
    file_path: str
    line: int
    severity: str          # CRITICAL | HIGH | MEDIUM | LOW | INFO
    category: str          # Security | Performance | Bug | Maintainability | Architecture
    title: str
    description: str
    code_example: str = ""
    auto_fixable: bool = False
    cwe: str = ""
    effort: str = "medium" # trivial | easy | medium | hard

    def to_github_comment(self) -> dict[str, Any]:
        severity_emoji = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🔵",
            "INFO": "ℹ️",
        }.get(self.severity, "⚪")

        body = textwrap.dedent(f"""
            {severity_emoji} **[{self.severity}] {self.title}**

            **Category:** {self.category}
            {f"**CWE:** {self.cwe}" if self.cwe else ""}
            **Effort to fix:** {self.effort}

            {self.description}
        """).strip()

        if self.code_example:
            body += f"\n\n```python\n{self.code_example}\n```"

        return {
            "path": self.file_path,
            "line": max(self.line, 1),
            "body": body,
            "side": "RIGHT",
        }


# ---------------------------------------------------------------------------
# Semgrep result parser
# ---------------------------------------------------------------------------

def parse_semgrep_results(semgrep_json_path: str) -> list[ReviewIssue]:
    """Convert Semgrep JSON output into ReviewIssue objects."""
    if not os.path.exists(semgrep_json_path):
        print(f"[semgrep] Results file not found: {semgrep_json_path} — skipping")
        return []

    with open(semgrep_json_path) as f:
        data = json.load(f)

    issues: list[ReviewIssue] = []
    for result in data.get("results", []):
        extra = result.get("extra", {})
        meta = extra.get("metadata", {})
        severity_map = {
            "ERROR": "HIGH",
            "WARNING": "MEDIUM",
            "INFO": "INFO",
        }
        issues.append(ReviewIssue(
            file_path=result.get("path", "unknown"),
            line=result.get("start", {}).get("line", 1),
            severity=severity_map.get(result.get("severity", "INFO"), "INFO"),
            category=meta.get("category", "Maintainability").capitalize(),
            title=result.get("check_id", "Semgrep finding").split(".")[-1].replace("-", " ").title(),
            description=extra.get("message", ""),
            cwe=meta.get("cwe", ""),
        ))

    print(f"[semgrep] Parsed {len(issues)} findings from {semgrep_json_path}")
    return issues


# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------

class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, token: str, repo: str, pr_number: int) -> None:
        self.token = token
        self.repo = repo
        self.pr_number = pr_number
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def get_pr_diff(self) -> str:
        """Fetch the unified diff for the PR."""
        url = f"{self.BASE}/repos/{self.repo}/pulls/{self.pr_number}"
        resp = self.session.get(url, headers={"Accept": "application/vnd.github.v3.diff"})
        resp.raise_for_status()
        return resp.text[:20_000]  # cap to avoid token overflow

    def get_latest_commit_sha(self) -> str:
        url = f"{self.BASE}/repos/{self.repo}/pulls/{self.pr_number}"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()["head"]["sha"]

    def post_review(self, issues: list[ReviewIssue], commit_sha: str) -> None:
        """Post a PR review with inline comments."""
        by_severity: dict[str, list[ReviewIssue]] = {}
        for issue in issues:
            by_severity.setdefault(issue.severity, []).append(issue)

        critical = len(by_severity.get("CRITICAL", []))
        high = len(by_severity.get("HIGH", []))

        summary_lines = ["## 🤖 AirAd AI Code Review\n"]
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = len(by_severity.get(sev, []))
            if count:
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "ℹ️"}[sev]
                summary_lines.append(f"- {emoji} **{sev}**: {count}")

        if not issues:
            summary_lines.append("\n✅ No issues found — looks good!")

        summary_lines.append(
            "\n\n*Powered by Semgrep + Claude (Anthropic). "
            "Review comments are AI-generated; always apply human judgement.*"
        )

        event = "REQUEST_CHANGES" if (critical + high) > 0 else "COMMENT"

        payload = {
            "commit_id": commit_sha,
            "body": "\n".join(summary_lines),
            "event": event,
            "comments": [i.to_github_comment() for i in issues if i.file_path != "unknown"],
        }

        url = f"{self.BASE}/repos/{self.repo}/pulls/{self.pr_number}/reviews"
        resp = self.session.post(url, json=payload)
        resp.raise_for_status()
        print(f"[github] Posted review (event={event}) with {len(issues)} comments")


# ---------------------------------------------------------------------------
# Claude AI review
# ---------------------------------------------------------------------------

def run_ai_review(
    diff: str,
    semgrep_issues: list[ReviewIssue],
    client: anthropic.Anthropic,
) -> list[ReviewIssue]:
    """Send diff + semgrep findings to Claude for deep contextual review."""

    semgrep_summary = json.dumps(
        [asdict(i) for i in semgrep_issues[:30]],  # cap to avoid token overflow
        indent=2,
    )

    prompt = textwrap.dedent(f"""
        You are performing a code review for **AirAd**, a hyperlocal vendor discovery platform.

        **Tech stack:**
        - Backend: Django 5.x, DRF 3.15, Python 3.12, PostgreSQL 16 + PostGIS, Redis, Celery 5.x, SimpleJWT
        - Frontend: React 18, TypeScript 5, Vite, Zustand, TanStack Query, React Router 6

        **Pull Request Diff (truncated to 20 000 chars):**
        ```diff
        {diff}
        ```

        **Semgrep Static Analysis Findings (already reported — do NOT duplicate these):**
        ```json
        {semgrep_summary}
        ```

        Perform a deep review focusing on issues that static analysis CANNOT catch:
        1. Business logic bugs and edge cases
        2. Authentication / authorisation flaws (IDOR, missing permission checks, JWT misuse)
        3. Django ORM performance issues (N+1, missing select_related, unbounded querysets)
        4. React state management bugs (stale closures, missing deps in useEffect)
        5. TypeScript type safety gaps (unsafe casts, missing null checks)
        6. API contract issues (missing validation, inconsistent error responses)
        7. Celery task reliability (missing retry logic, non-idempotent tasks)
        8. Missing test coverage for critical paths

        For each issue return a JSON object with EXACTLY these keys:
        - file_path (string)
        - line (integer, best estimate from diff)
        - severity (one of: CRITICAL, HIGH, MEDIUM, LOW, INFO)
        - category (one of: Security, Performance, Bug, Maintainability, Architecture)
        - title (string, ≤80 chars)
        - description (string, 2-4 sentences explaining the problem and impact)
        - code_example (string, a concrete fix — empty string if not applicable)
        - auto_fixable (boolean)
        - cwe (string, e.g. "CWE-89" — empty string if not applicable)
        - effort (one of: trivial, easy, medium, hard)

        Return ONLY a valid JSON array. No markdown, no prose outside the array.
        If there are no additional issues beyond what Semgrep found, return an empty array [].
    """).strip()

    print("[claude] Sending diff to Claude for AI review...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8000,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.content[0].text.strip()

    # Strip markdown code fences if Claude wrapped the JSON
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        raw_issues = json.loads(content)
    except json.JSONDecodeError as exc:
        print(f"[claude] Failed to parse JSON response: {exc}")
        print(f"[claude] Raw response:\n{content[:500]}")
        return []

    issues: list[ReviewIssue] = []
    for item in raw_issues:
        try:
            issues.append(ReviewIssue(**{k: item.get(k, "") for k in ReviewIssue.__dataclass_fields__}))
        except TypeError as exc:
            print(f"[claude] Skipping malformed issue: {exc} — {item}")

    print(f"[claude] AI review returned {len(issues)} additional findings")
    return issues


# ---------------------------------------------------------------------------
# Quality gate
# ---------------------------------------------------------------------------

def quality_gate(issues: list[ReviewIssue]) -> int:
    """Return exit code: 1 if CRITICAL issues exist, else 0."""
    critical = [i for i in issues if i.severity == "CRITICAL"]
    high = [i for i in issues if i.severity == "HIGH"]

    if critical:
        print(f"\n❌ Quality gate FAILED — {len(critical)} CRITICAL issue(s) found:")
        for i in critical:
            print(f"   [{i.file_path}:{i.line}] {i.title}")
        return 1

    if high:
        print(f"\n⚠️  Quality gate WARNING — {len(high)} HIGH issue(s) found (not blocking):")
        for i in high:
            print(f"   [{i.file_path}:{i.line}] {i.title}")

    print(f"\n✅ Quality gate PASSED — {len(issues)} total finding(s), none CRITICAL")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AirAd AI Code Review — Semgrep + Claude orchestrator"
    )
    parser.add_argument("--pr-number", type=int, required=True, help="GitHub PR number")
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/name format")
    parser.add_argument(
        "--semgrep-results",
        default="semgrep.json",
        help="Path to Semgrep JSON output (default: semgrep.json)",
    )
    parser.add_argument(
        "--output",
        default="review-comments.json",
        help="Path to write combined review JSON (default: review-comments.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print findings without posting to GitHub",
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip Claude AI review (Semgrep only)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    github_token = os.environ.get("GITHUB_TOKEN")

    if not args.dry_run and not github_token:
        print("ERROR: GITHUB_TOKEN environment variable is required (unless --dry-run)")
        sys.exit(1)

    if not args.skip_ai and not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable is required (unless --skip-ai)")
        sys.exit(1)

    # 1. Parse Semgrep findings
    semgrep_issues = parse_semgrep_results(args.semgrep_results)

    # 2. Fetch PR diff and run AI review
    ai_issues: list[ReviewIssue] = []
    diff = ""

    if not args.skip_ai and anthropic_key:
        if not args.dry_run and github_token:
            gh = GitHubClient(github_token, args.repo, args.pr_number)
            try:
                diff = gh.get_pr_diff()
                print(f"[github] Fetched diff ({len(diff)} chars)")
            except requests.HTTPError as exc:
                print(f"[github] Failed to fetch diff: {exc} — skipping AI review")
        else:
            print("[dry-run] Skipping GitHub diff fetch")

        if diff:
            claude_client = anthropic.Anthropic(api_key=anthropic_key)
            ai_issues = run_ai_review(diff, semgrep_issues, claude_client)

    # 3. Combine and deduplicate
    all_issues = semgrep_issues + ai_issues
    print(f"\n[review] Total findings: {len(all_issues)} "
          f"(semgrep={len(semgrep_issues)}, ai={len(ai_issues)})")

    # 4. Write combined output
    with open(args.output, "w") as f:
        json.dump([asdict(i) for i in all_issues], f, indent=2)
    print(f"[review] Written to {args.output}")

    # 5. Post to GitHub (unless dry-run)
    if not args.dry_run and github_token:
        gh = GitHubClient(github_token, args.repo, args.pr_number)
        commit_sha = gh.get_latest_commit_sha()
        gh.post_review(all_issues, commit_sha)
    else:
        print("\n[dry-run] Review findings:")
        for issue in all_issues:
            print(f"  [{issue.severity}] {issue.file_path}:{issue.line} — {issue.title}")

    # 6. Quality gate
    exit_code = quality_gate(all_issues)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
