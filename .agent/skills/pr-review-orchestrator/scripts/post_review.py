#!/usr/bin/env python3
"""
Submit a batched GitHub pull request review based on the review matrix.

Usage: python3 post_review.py <PR_NUMBER>
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(".agent/skills/pr-review-orchestrator")
TMP_DIR = BASE_DIR / "tmp"

MATRIX_FILE = TMP_DIR / "review-matrix.json"
RUNTIME_FILE = TMP_DIR / "runtime-summary.json"
PAYLOAD_FILE = TMP_DIR / "review-payload.json"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def load_json(path: Path) -> list | dict | None:
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def get_pr_details(pr_number: str) -> tuple[str, str]:
    """Returns (headRefOid, author_login)."""
    result = run([
        "gh", "pr", "view", pr_number,
        "--json", "headRefOid,author",
        "--jq", "[.headRefOid, .author.login] | join(\"|\")"
    ])
    parts = result.split("|")
    return parts[0], parts[1] if len(parts) > 1 else "unknown"


def get_current_user() -> str:
    return run(["gh", "api", "user", "--jq", ".login"])


def classify_overall_risk(issues: list[dict], runtime: dict | None) -> str:
    if runtime:
        if runtime.get("build") == "FAIL" or runtime.get("tests") == "FAIL":
            return "HIGH RISK"

    severities = [i.get("severity", "LOW") for i in issues]
    if "HIGH" in severities:
        return "HIGH RISK"
    if "MEDIUM" in severities:
        return "MEDIUM RISK"
    if issues:
        return "LOW RISK"
    return "SAFE"


def build_inline_comment(issue: dict) -> dict:
    severity = issue["severity"]
    category = issue["category"]
    message = issue["message"]

    body = f"""**Status: ⚠️ CHANGES REQUESTED**
**Severity:** {severity}
**Category:** {category}

**Problem:**
{message}

**Required Fix:**
Apply corrective change aligned with project standards and engineering guidelines."""

    comment = {
        "path": issue["path"],
        "side": "RIGHT",
        "body": body,
    }

    # Use 'line' or 'position' depending on what's available
    if issue.get("line"):
        comment["line"] = issue["line"]

    return comment


def build_review_body(runtime: dict | None, issues: list[dict], risk_level: str) -> str:
    lines = [f"## Code Review\n\n**Overall Risk:** {risk_level}\n"]

    if runtime:
        lines.append("### Runtime Validation\n")
        status_emoji = {"PASS": "✅", "FAIL": "❌", "N/A": "⏭"}
        for key in ("build", "lint", "typecheck", "tests", "runtime"):
            val = runtime.get(key, "N/A")
            emoji = status_emoji.get(val, "❓")
            lines.append(f"- **{key.title()}:** {emoji} {val}")
        lines.append("")

    if not issues:
        lines.append("### Summary\n\nNo issues detected in modified files. All validation passes. ✅")
    else:
        count = len(issues)
        high = sum(1 for i in issues if i.get("severity") == "HIGH")
        med = sum(1 for i in issues if i.get("severity") == "MEDIUM")
        low = sum(1 for i in issues if i.get("severity") == "LOW")
        lines.append(f"### Summary\n\n{count} issue(s) found: {high} HIGH, {med} MEDIUM, {low} LOW\n\nSee inline comments for details.")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: post_review.py <PR_NUMBER>", file=sys.stderr)
        sys.exit(1)

    pr_number = sys.argv[1]

    if not MATRIX_FILE.exists():
        print(f"ERROR: Review matrix not found at {MATRIX_FILE}", file=sys.stderr)
        sys.exit(1)

    issues = load_json(MATRIX_FILE) or []
    runtime = load_json(RUNTIME_FILE)

    commit_sha, pr_author = get_pr_details(pr_number)

    try:
        current_user = get_current_user()
    except subprocess.CalledProcessError:
        current_user = None
        print("WARNING: Could not determine current user — using COMMENT event", file=sys.stderr)

    # Determine review event
    # Can't approve/request_changes on own PR
    own_pr = current_user and (pr_author == current_user)
    if own_pr:
        event = "COMMENT"
    elif issues:
        event = "REQUEST_CHANGES"
    else:
        event = "APPROVE"

    risk_level = classify_overall_risk(issues, runtime)
    comments = [build_inline_comment(issue) for issue in issues]

    review_payload = {
        "commit_id": commit_sha,
        "event": event,
        "body": build_review_body(runtime, issues, risk_level),
        "comments": comments,
    }

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    with open(PAYLOAD_FILE, "w") as f:
        json.dump(review_payload, f, indent=2)

    print(f"Submitting review for PR #{pr_number} ({event}, {risk_level})...")
    print(f"  {len(comments)} inline comment(s)")

    run([
        "gh", "api",
        f"repos/{{owner}}/{{repo}}/pulls/{pr_number}/reviews",
        "--method", "POST",
        "--input", str(PAYLOAD_FILE)
    ])

    print(f"✅ Review submitted — {event}")

    # Cleanup
    for f in [PAYLOAD_FILE, MATRIX_FILE, RUNTIME_FILE]:
        if f.exists():
            f.unlink()


if __name__ == "__main__":
    main()
