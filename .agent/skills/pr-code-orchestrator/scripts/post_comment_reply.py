#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(".agent/skills/pr-code-orchestrator")
TMP_DIR = BASE_DIR / "tmp"

MATRIX_FILE = TMP_DIR / "pr-code-orchestrator-matrix.json"


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def load_matrix():
    if not MATRIX_FILE.exists():
        print("Matrix file not found.")
        sys.exit(1)

    with open(MATRIX_FILE, "r") as f:
        return json.load(f)


def create_issue(pr_number, entry):
    result = run([
        "gh", "issue", "create",
        "--title", f"Follow-up (PR #{pr_number}): {entry['classification']} comment",
        "--body",
        f"""Context:
- Origin PR: #{pr_number}
- Comment: {entry['comment_url']}
- Reason: Out of scope for current PR.""",
        "--label", "refactor"
    ])
    issue_url = result.stdout.strip()
    issue_number = issue_url.split("/")[-1]
    return issue_number


def build_body(entry):
    status = entry["status"].replace("_", " ")

    commit = entry.get("commit_sha") or "N/A"
    issue_number = entry.get("issue_number")

    body_lines = [
        f"Status: {status}",
        f"Commit: {commit}",
        "",
        "Summary:",
    ]

    if status == "NEW ISSUE" and issue_number:
        body_lines.append(f"- Tracked in issue #{issue_number}")
    elif status == "SOLVED":
        body_lines.append("- Changes implemented and validated.")
    elif status == "UNSOLVED":
        body_lines.append("- Unable to safely implement within current constraints.")
    elif status == "SKIPPED":
        body_lines.append("- Feedback invalid or already addressed.")

    return "\n".join(body_lines)


def reply_to_comment(entry, body):
    run([
        "gh", "api",
        f"repos/:owner/:repo/pulls/comments/{entry['comment_id']}/replies",
        "-f", f"body={body}"
    ])


def main():
    if len(sys.argv) != 2:
        print("Usage: post_comment_replies.py <PR_NUMBER>")
        sys.exit(1)

    pr_number = sys.argv[1]
    matrix = load_matrix()

    for entry in matrix:

        if entry["status"] == "NEW_ISSUE":
            issue_number = create_issue(pr_number, entry)
            entry["issue_number"] = issue_number

        body = build_body(entry)
        reply_to_comment(entry, body)

    # Persist updated matrix (with issue numbers)
    with open(MATRIX_FILE, "w") as f:
        json.dump(matrix, f)


if __name__ == "__main__":
    main()
