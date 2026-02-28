#!/usr/bin/env python3
"""
Score and rank issues by priority using the multi-axis scoring model.
Reads raw-issues.json and open-prs.json from tmp/, writes scored issue-matrix.json.

Usage: python3 score_issues.py
"""

import json
import re
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(".agent/skills/issue-task-orchestrator")
TMP_DIR = Path(".agent/tmp")


def load_json(path: Path) -> list | dict:
    if not path.exists():
        print(f"WARNING: {path} not found, returning empty", file=sys.stderr)
        return []
    with open(path) as f:
        return json.load(f)

def fetch_gh_json(command: list[str]) -> list | dict:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error fetching data with {' '.join(command)}: {e}")
        return []


def detect_classification(issue: dict) -> str:
    labels = [l["name"].lower() for l in issue.get("labels", [])]
    title = issue.get("title", "").lower()
    body = (issue.get("body") or "").lower()

    if any(l in labels for l in ["bug", "fix", "crash", "error"]):
        return "BUG"
    if any(l in labels for l in ["enhancement", "feature", "feat"]):
        return "FEATURE"
    if any(l in labels for l in ["refactor", "cleanup", "tech-debt", "debt"]):
        return "REFACTOR"
    if any(l in labels for l in ["docs", "documentation"]):
        return "DOC"
    if any(l in labels for l in ["duplicate", "wontfix", "invalid"]):
        return "INVALID"
    if "duplicate" in title or "duplicate" in body:
        return "DUPLICATE"
    if re.search(r"\bfix\b|\bbug\b|\bcrash\b|\berror\b|\bbroken\b", title):
        return "BUG"
    if re.search(r"\badd\b|\bimplement\b|\bfeat\b|\bnew\b|\bcreate\b", title):
        return "FEATURE"
    return "FEATURE"  # default


def score_issue(issue: dict, classification: str) -> float:
    """
    Scoring axes (0-10 each):
    - User Impact (weight x2)
    - Effort inverse (10 = quick)
    - Dependency unblock (weight x1.5)
    - Risk if delayed
    Total max = 50
    """
    title = issue.get("title", "").lower()
    body = (issue.get("body") or "").lower()
    labels = [l["name"].lower() for l in issue.get("labels", [])]

    # User Impact
    impact = 5
    if any(w in title + body for w in ["crash", "data loss", "security", "auth", "payment", "broken"]):
        impact = 10
    elif any(w in title + body for w in ["error", "fail", "cannot", "unable", "wrong"]):
        impact = 7
    elif classification == "DOC":
        impact = 2
    elif classification == "REFACTOR":
        impact = 3

    # Effort (inverse — quick wins score higher)
    effort = 5
    if any(w in title + body for w in ["typo", "rename", "update string", "change text", "small", "quick"]):
        effort = 9
    elif any(w in title + body for w in ["refactor", "rewrite", "migrate", "redesign", "overhaul"]):
        effort = 2
    elif any(l in labels for l in ["good first issue", "easy", "quick"]):
        effort = 8

    # Dependency unblock
    unblock = 0
    if "blocks" in body or "blocked by" in body:
        unblock = 7
    elif re.search(r"#\d+", body):
        unblock = 3  # references other issues

    # Risk if delayed
    risk = 3
    if any(w in title + body for w in ["security", "vulnerability", "cve", "xss", "injection"]):
        risk = 10
    elif any(w in title + body for w in ["compliance", "gdpr", "legal", "privacy"]):
        risk = 9
    elif classification == "BUG":
        risk = 6
    elif classification == "DOC":
        risk = 1

    score = (impact * 2) + effort + (unblock * 1.5) + risk
    return round(score, 1)


def is_in_active_pr(issue_number: int, open_prs: list) -> bool:
    pattern = f"#{issue_number}"
    for pr in open_prs:
        if pattern in (pr.get("body") or "") or pattern in pr.get("title", ""):
            return True
    return False


def main() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching repository data. This replaces bash CLI steps...")
    raw_issues = fetch_gh_json(["gh", "issue", "list", "--state", "open", "--limit", "200", "--json", "number,title,body,labels,assignees,milestone,createdAt,updatedAt"])
    open_prs = fetch_gh_json(["gh", "pr", "list", "--state", "open", "--json", "number,title,body"])
    recent_merged = fetch_gh_json(["gh", "pr", "list", "--state", "merged", "--limit", "20", "--json", "number,title,mergedAt,body"])

    # Build set of recently-resolved issue numbers from merged PR bodies
    resolved_refs = set()
    for pr in recent_merged:
        body = pr.get("body") or ""
        for match in re.findall(r"(?:closes|fixes|resolves)\s+#(\d+)", body, re.IGNORECASE):
            resolved_refs.add(int(match))

    matrix = []
    for issue in raw_issues:
        number = issue["number"]
        classification = detect_classification(issue)
        in_pr = is_in_active_pr(number, open_prs)

        # Determine initial status
        if number in resolved_refs:
            status = "ALREADY_RESOLVED"
        elif in_pr:
            status = "ALREADY_RESOLVED"
        elif classification == "INVALID":
            status = "INVALID"
        elif classification in ("DUPLICATE",):
            status = "INVALID"
        else:
            status = "CONFIRMED"  # default — engineering validation will refine

        priority_score = score_issue(issue, classification) if status == "CONFIRMED" else 0.0

        matrix.append({
            "issue_number": number,
            "title": issue.get("title", ""),
            "classification": classification,
            "status": status,
            "priority_score": priority_score,
            "in_active_pr": in_pr,
            "confirmed": status == "CONFIRMED",
            "labels": [l["name"] for l in issue.get("labels", [])],
        })

    # Sort by priority score descending
    matrix.sort(key=lambda x: x["priority_score"], reverse=True)

    out = TMP_DIR / "issue-matrix.json"
    with open(out, "w") as f:
        json.dump(matrix, f, indent=2)

    # Print ranked summary
    print(f"\n{'Rank':<5} {'Score':<7} {'#':<6} {'Status':<22} {'Title'}")
    print("-" * 80)
    rank = 1
    for item in matrix:
        if item["status"] == "CONFIRMED":
            print(f"{rank:<5} {item['priority_score']:<7} #{item['issue_number']:<5} {item['status']:<22} {item['title'][:45]}")
            rank += 1

    print(f"\n✅ Matrix written to {out}")
    print(f"   {sum(1 for i in matrix if i['status'] == 'CONFIRMED')} confirmed, "
          f"{sum(1 for i in matrix if i['status'] != 'CONFIRMED')} skipped/resolved")


if __name__ == "__main__":
    main()
