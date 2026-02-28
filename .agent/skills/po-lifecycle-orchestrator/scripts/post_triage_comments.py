#!/usr/bin/env python3
"""
PO Lifecycle — Post Triage Comments to GitHub Issues

Reads triage-matrix.json and posts one structured status comment per issue.
Only posts to real GitHub issues (skips synthetic items).

Usage:
  python3 post_triage_comments.py \
    --matrix tmp/triage-matrix.json \
    [--dry-run]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


BUCKET_LABELS = {
    "TASKS":  ("🔴", "TASKS — Priority",    "Immediate action — in current sprint"),
    "TODO":   ("🟡", "TODO — Next Sprint",   "Queued for next sprint"),
    "BACKLOG":("🔵", "BACKLOG — Long-term",  "Deferred — needs design or lower priority"),
    "SKIP":   ("✅", "SKIP",                 "Already handled or not applicable"),
}


def post_comment(issue_number: int, body: str, dry_run: bool) -> bool:
    if dry_run:
        print(f"  [DRY RUN] Would post to #{issue_number}:")
        print(f"  {body[:120]}...")
        return True

    result = subprocess.run(
        ["gh", "issue", "comment", str(issue_number), "--body", body],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ❌ Failed to post to #{issue_number}: {result.stderr.strip()}")
        return False
    return True


def format_comment(item: dict) -> str:
    bucket = item.get("bucket", "BACKLOG")
    icon, label, description = BUCKET_LABELS.get(bucket, ("📋", bucket, ""))
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reason = item.get("reason_text", "")

    return f"""**{icon} PO Triage — {today}**

**Bucket:** {label}
**Status:** {description}
**Reason:** {reason}

> Triaged automatically by PO Lifecycle Orchestrator.
> Update label `triage:tasks`, `triage:todo`, or `triage:backlog` to override."""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True, help="Path to triage-matrix.json")
    parser.add_argument("--dry-run", action="store_true", help="Print comments without posting")
    args = parser.parse_args()

    matrix_path = Path(args.matrix)
    if not matrix_path.exists():
        print(f"ERROR: Matrix not found: {matrix_path}", file=sys.stderr)
        sys.exit(1)

    matrix = json.loads(matrix_path.read_text())
    real_items = [m for m in matrix if not m.get("synthetic", False) and m.get("bucket") != "SKIP"]

    print(f"Posting triage comments to {len(real_items)} issues...")
    if args.dry_run:
        print("(DRY RUN — no actual posts)\n")

    success = 0
    failed = 0

    for item in real_items:
        number = item.get("number")
        title = item.get("title", "")
        bucket = item.get("bucket", "BACKLOG")

        print(f"  #{number} [{bucket}] {title[:50]}")
        body = format_comment(item)

        if post_comment(number, body, args.dry_run):
            success += 1
        else:
            failed += 1

    print(f"\n{'─' * 40}")
    print(f"  ✅ Posted: {success}")
    print(f"  ❌ Failed: {failed}")


if __name__ == "__main__":
    main()
