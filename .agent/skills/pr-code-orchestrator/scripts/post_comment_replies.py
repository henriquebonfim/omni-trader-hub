#!/usr/bin/env python3
"""
Post structured status replies to PR review comments based on the code matrix.

Usage: python3 post_comment_replies.py <PR_NUMBER>
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(".agent/skills/pr-code-orchestrator")
TMP_DIR = Path(".agent/tmp")
MATRIX_FILE = TMP_DIR / "pr-code-matrix.json"


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def load_matrix() -> list[dict]:
    if not MATRIX_FILE.exists():
        print(f"ERROR: Matrix file not found at {MATRIX_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(MATRIX_FILE) as f:
        return json.load(f)


def create_followup_issue(pr_number: str, entry: dict) -> str:
    """Create a GitHub issue for out-of-scope comments. Returns issue number."""
    comment_url = entry.get("comment_url", "unknown")
    classification = entry.get("classification", "OUT_OF_SCOPE")

    body = f"""## Context

This item was raised as a review comment on PR #{pr_number} but is out of scope for that change and requires separate handling.

**Original comment:** {comment_url}
**Classification:** {classification}
**File:** `{entry.get('path', 'N/A')}` line {entry.get('line', 'N/A')}

## Why separate

The requested change exceeds the scope of PR #{pr_number}. Implementing it here would introduce unreviewed scope creep.

## Next steps

Review this issue and schedule in the appropriate sprint/milestone.
"""
    body_file = TMP_DIR / f"issue-body-{pr_number}.md"
    body_file.write_text(body)

    result = run([
        "gh", "issue", "create",
        "--title", f"Follow-up from PR #{pr_number}: {classification} — {entry.get('path', 'unknown')}:{entry.get('line', '?')}",
        "--body-file", str(body_file),
        "--label", "follow-up,technical-debt"
    ])
    body_file.unlink()
    issue_url = result.strip()
    return issue_url.split("/")[-1]  # Extract issue number from URL


def build_reply_body(entry: dict) -> str:
    status = entry["status"]
    commit_sha = entry.get("commit_sha") or "N/A"
    issue_number = entry.get("issue_number")

    if status == "SOLVED":
        return f"""**Status: ✅ SOLVED**
Commit: `{commit_sha}`

**Summary:**
- Implementation validated and committed
- Relevant tests added/updated
- No regressions introduced"""

    elif status == "UNSOLVED":
        return f"""**Status: ❌ UNSOLVED**

**Reason:** Unable to safely implement within current constraints.
**Blocker:** Requires further investigation or architectural decision before proceeding."""

    elif status == "NEW_ISSUE":
        issue_ref = f"#{issue_number}" if issue_number else "pending"
        return f"""**Status: 🆕 NEW ISSUE**
Issue: {issue_ref}

**Reason:** This change exceeds the scope of the current PR and has been tracked as a separate issue for proper review and scheduling."""

    elif status == "SKIPPED":
        return """**Status: ⏭ SKIPPED**

**Reason:** Feedback is invalid, already addressed, or outdated."""

    elif status == "SOLVED" and entry.get("classification") == "CLARIFICATION_ONLY":
        return """**Status: ✅ ADDRESSED**

This was a clarification question — answered inline. No code change required."""

    else:
        return f"**Status: {status}**\n\nManual follow-up required."


def reply_to_comment(comment_id: str, body: str) -> None:
    """Post a reply to an inline PR review comment."""
    payload = {"body": body}
    payload_file = TMP_DIR / f"comment-reply-{comment_id}.json"
    with open(payload_file, "w") as f:
        json.dump(payload, f)

    run([
        "gh", "api",
        "repos/{owner}/{repo}/pulls/comments/{id}/replies".replace("{id}", str(comment_id)),
        "--method", "POST",
        "--input", str(payload_file)
    ])
    payload_file.unlink()


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: post_comment_replies.py <PR_NUMBER>", file=sys.stderr)
        sys.exit(1)

    pr_number = sys.argv[1]
    matrix = load_matrix()
    total = len(matrix)
    print(f"Processing {total} comment(s) from matrix for PR #{pr_number}...\n")

    for i, entry in enumerate(matrix, 1):
        comment_id = entry["comment_id"]
        status = entry["status"]
        path = entry.get("path", "?")
        line = entry.get("line", "?")
        print(f"[{i}/{total}] {status:<12} {path}:{line} (comment {comment_id})")

        # Create issue for out-of-scope items
        if status == "NEW_ISSUE" and not entry.get("issue_number"):
            print(f"  → Creating follow-up issue...")
            try:
                issue_number = create_followup_issue(pr_number, entry)
                entry["issue_number"] = issue_number
                print(f"  → Created issue #{issue_number}")
            except subprocess.CalledProcessError as e:
                print(f"  → WARNING: Failed to create issue: {e.stderr}", file=sys.stderr)

        # Post reply
        body = build_reply_body(entry)
        try:
            reply_to_comment(comment_id, body)
            print(f"  → Reply posted")
        except subprocess.CalledProcessError as e:
            print(f"  → ERROR posting reply: {e.stderr}", file=sys.stderr)

    # Persist updated matrix (with issue numbers filled in)
    with open(MATRIX_FILE, "w") as f:
        json.dump(matrix, f, indent=2)

    print(f"\n✅ Done. Processed {total} comment(s).")


if __name__ == "__main__":
    main()
