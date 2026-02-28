#!/usr/bin/env python3
"""
Post structured status comments to GitHub issues based on the issue matrix.
Usage: python3 post_issue_comments.py
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(".agent/skills/issue-task-orchestrator")
TMP_DIR = Path(".agent/tmp")
MATRIX_FILE = TMP_DIR / "issue-matrix.json"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def load_matrix() -> list[dict]:
    if not MATRIX_FILE.exists():
        print(f"ERROR: Matrix file not found at {MATRIX_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(MATRIX_FILE) as f:
        return json.load(f)


def build_comment_body(issue: dict) -> str:
    status = issue["status"]
    number = issue["issue_number"]
    score = issue.get("priority_score", "N/A")

    if status == "CONFIRMED":
        scope = issue.get("scope", ["Implementation scope TBD"])
        scope_lines = "\n".join(f"- {s}" for s in scope) if isinstance(scope, list) else f"- {scope}"
        return f"""**Status: ✅ CONFIRMED TASK**

**Scope:**
{scope_lines}

**Priority Score:** {score}/40

**PR:** Will be included in upcoming batch PR — work begins shortly."""

    elif status == "NEEDS_CLARIFICATION":
        missing = issue.get("missing", ["Additional details required"])
        missing_lines = "\n".join(f"- {m}" for m in missing) if isinstance(missing, list) else f"- {missing}"
        return f"""**Status: ❌ NEEDS CLARIFICATION**

**Missing information before this can be actioned:**
{missing_lines}

Please reply with the details above so we can prioritize this."""

    elif status == "ALREADY_RESOLVED":
        evidence = issue.get("evidence", "See recent commits/PRs")
        return f"""**Status: 🟢 ALREADY RESOLVED**

**Evidence:** {evidence}

Closing this issue as it appears to be addressed. If the problem persists, please reopen with updated details."""

    elif status == "INVALID":
        reason = issue.get("reason", "Does not meet criteria for action")
        return f"""**Status: ⏭ INVALID / WON'T FIX**

**Reason:** {reason}"""

    else:
        return f"**Status: ❓ UNCLASSIFIED** — Manual review required."


def post_comment(issue_number: int, body: str) -> None:
    print(f"  → Posting comment to issue #{issue_number}...")
    body_file = TMP_DIR / f"issue-comment-{issue_number}.md"
    body_file.write_text(body)
    try:
        run(["gh", "issue", "comment", str(issue_number), "--body-file", str(body_file)])
    finally:
        if body_file.exists():
            body_file.unlink()


def close_if_needed(issue: dict) -> None:
    status = issue["status"]
    number = issue["issue_number"]

    if status == "ALREADY_RESOLVED":
        print(f"  → Closing issue #{number} (already resolved)...")
        run(["gh", "issue", "close", str(number),
             "--reason", "completed",
             "--comment", "Closing — resolved in a recent PR/commit. Reopen if the issue persists."])

    elif status == "INVALID":
        print(f"  → Closing issue #{number} (invalid)...")
        run(["gh", "issue", "close", str(number), "--reason", "not planned"])


def main() -> None:
    matrix = load_matrix()
    total = len(matrix)
    print(f"Processing {total} issues from matrix...\n")

    for i, issue in enumerate(matrix, 1):
        number = issue["issue_number"]
        status = issue["status"]
        title = issue.get("title", "")[:60]
        print(f"[{i}/{total}] #{number} [{status}] {title}")

        body = build_comment_body(issue)
        post_comment(number, body)
        close_if_needed(issue)

    print(f"\n✅ Done. Processed {total} issues.")


if __name__ == "__main__":
    main()
