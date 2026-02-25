#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(".agent/skills/pr-review-orchestrator")
TMP_DIR = BASE_DIR / "tmp"

MATRIX_FILE = TMP_DIR / "pr-review-orchestrator-matrix.json"
RUNTIME_FILE = TMP_DIR / "runtime-summary.json"
PAYLOAD_FILE = TMP_DIR / "review_payload.json"


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def get_commit_sha(pr_number):
    result = run([
        "gh", "pr", "view", pr_number,
        "--json", "headRefOid"
    ])
    return json.loads(result.stdout)["headRefOid"]


def load_json(path):
    if not path.exists():
        return None
    with open(path, "r") as f:
        return json.load(f)


def build_comment(issue):
    return {
        "path": issue["path"],
        "line": issue["line"],
        "side": "RIGHT",
        "body": f"""Status: ⚠️ CHANGES REQUESTED
Severity: {issue["severity"]}
Category: {issue["category"]}

Problem:
- {issue["message"]}

Required Fix:
- Apply corrective change aligned with project standards."""
    }


def build_review_body(runtime_summary, issue_count):
    lines = []

    if runtime_summary:
        lines.append("Runtime Validation Summary:")
        for k, v in runtime_summary.items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    if issue_count == 0:
        lines.append("No issues detected in modified files.")
    else:
        lines.append(f"{issue_count} issue(s) detected in changed files.")

    return "\n".join(lines)


def main():
    if len(sys.argv) != 2:
        print("Usage: post_review.py <PR_NUMBER>")
        sys.exit(1)

    pr_number = sys.argv[1]

    if not MATRIX_FILE.exists():
        print("Matrix file not found.")
        sys.exit(1)

    issues = load_json(MATRIX_FILE) or []
    runtime_summary = load_json(RUNTIME_FILE)

    commit_sha = get_commit_sha(pr_number)

    comments = [build_comment(issue) for issue in issues]

    review_payload = {
        "commit_id": commit_sha,
        "event": "REQUEST_CHANGES" if issues else "APPROVE",
        "body": build_review_body(runtime_summary, len(issues)),
        "comments": comments
    }

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    with open(PAYLOAD_FILE, "w") as f:
        json.dump(review_payload, f)

    subprocess.run([
        "gh", "api",
        f"repos/:owner/:repo/pulls/{pr_number}/reviews",
        "--input", str(PAYLOAD_FILE)
    ], check=True)

    # Cleanup
    for file in [PAYLOAD_FILE, MATRIX_FILE, RUNTIME_FILE]:
        if file.exists():
            file.unlink()


if __name__ == "__main__":
    main()
