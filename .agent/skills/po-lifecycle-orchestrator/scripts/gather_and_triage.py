#!/usr/bin/env python3
"""
PO Lifecycle — Aggregation and Triage Engine

Reads all source files (issues, PRs, docker health, test health, visual review),
applies triage rules, and produces triage-matrix.json + three planning files.

Usage:
  python3 gather_and_triage.py \
    --issues     tmp/gh-issues-open.json \
    --closed     tmp/gh-issues-closed.json \
    --prs        tmp/open-prs.json \
    --merged     tmp/merged-prs.json \
    --docker     tmp/docker-health.json \
    --tests      tmp/test-health.json \
    --visual     tmp/visual-review.json \
    --context    tmp/project-context.json \
    --output-dir tmp/
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def load_json(path: str | None, default=None):
    if not path:
        return default
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def days_old(date_str: str | None) -> int:
    """Return how many days ago an ISO date string is."""
    if not date_str:
        return 0
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return delta.days
    except Exception:
        return 0


def get_label_names(issue: dict) -> list[str]:
    labels = issue.get("labels", [])
    return [
        (lb.get("name") if isinstance(lb, dict) else str(lb)).lower()
        for lb in labels
    ]


def get_merged_issue_refs(merged_prs: list[dict]) -> set[int]:
    """Extract issue numbers referenced in merged PR bodies."""
    refs: set[int] = set()
    for pr in merged_prs:
        body = pr.get("body", "") or ""
        for match in re.findall(r"[Cc]loses?\s*#(\d+)", body):
            refs.add(int(match))
        for match in re.findall(r"[Ff]ixes?\s*#(\d+)", body):
            refs.add(int(match))
    return refs


def get_in_flight_issues(open_prs: list[dict]) -> set[int]:
    """Extract issue numbers referenced in open PR branch names / titles."""
    refs: set[int] = set()
    for pr in open_prs:
        # Branch name often contains issue number
        branch = pr.get("headRefName", "") or ""
        for m in re.findall(r"(\d+)", branch):
            refs.add(int(m))
        title = pr.get("title", "") or ""
        for m in re.findall(r"#(\d+)", title):
            refs.add(int(m))
    return refs


# ─── TRIAGE RULES ─────────────────────────────────────────────────────────────

TASKS_LABELS = {
    "priority: critical", "priority:critical", "critical",
    "priority: high", "priority:high",
    "security", "data-loss", "blocker", "p0", "p1",
}

TODO_LABELS = {
    "priority: medium", "priority:medium", "medium",
    "confirmed", "ready", "sprint", "p2",
}

BACKLOG_LABELS = {
    "enhancement", "idea", "question", "discussion", "design-needed",
    "needs-spec", "help wanted", "good first issue",
    "wontfix", "won't fix", "invalid", "duplicate",
    "tech-debt", "long-term", "future", "backlog",
}

SKIP_LABELS = {"wontfix", "won't fix", "invalid", "duplicate", "spam"}

OVERRIDE_LABELS = {
    "triage:tasks": "TASKS",
    "triage:todo": "TODO",
    "triage:backlog": "BACKLOG",
}


def triage_issue(
    issue: dict,
    closed_issue_numbers: set[int],
    merged_issue_refs: set[int],
    in_flight_issues: set[int],
    docker_status: str,
    test_status: str,
) -> dict:
    number = issue.get("number", 0)
    title = issue.get("title", "")
    labels = get_label_names(issue)
    age_days = days_old(issue.get("createdAt"))
    last_update_days = days_old(issue.get("updatedAt"))

    # ── Skip checks ────────────────────────────────────────────────
    if number in merged_issue_refs:
        return _result(number, title, labels, "SKIP", "already-fixed", "Resolved by merged PR")
    if number in in_flight_issues:
        return _result(number, title, labels, "SKIP", "in-flight", "Open PR in progress")
    if any(lb in SKIP_LABELS for lb in labels):
        return _result(number, title, labels, "SKIP", "invalid", "Marked wontfix/invalid")

    # ── Manual override ────────────────────────────────────────────
    for override_label, bucket in OVERRIDE_LABELS.items():
        if override_label in labels:
            return _result(number, title, labels, bucket, "manual-override", f"Label: {override_label}")

    # ── TASKS bucket ───────────────────────────────────────────────
    # Security / critical
    if any(lb in TASKS_LABELS for lb in labels):
        return _result(number, title, labels, "TASKS", "high-priority-label", f"Label: {[l for l in labels if l in TASKS_LABELS]}")

    # Bug keywords in title with high impact
    title_lower = title.lower()
    if any(w in title_lower for w in ["crash", "broken", "down", "outage", "critical", "security", "data loss", "cannot login", "payment"]):
        return _result(number, title, labels, "TASKS", "critical-keyword", "Critical keyword in title")

    # Active milestone
    milestone = issue.get("milestone")
    if milestone and isinstance(milestone, dict):
        due = milestone.get("dueOn") or milestone.get("due_on")
        if due:
            due_days = days_old(due)
            if due_days >= 0:  # Due in the past or soon
                return _result(number, title, labels, "TASKS", "milestone-overdue", f"Milestone past due: {due}")

    # ── TODO bucket ────────────────────────────────────────────────
    if any(lb in TODO_LABELS for lb in labels):
        return _result(number, title, labels, "TODO", "sprint-label", f"Label: {[l for l in labels if l in TODO_LABELS]}")

    # Bug label (but not critical)
    if "bug" in labels:
        return _result(number, title, labels, "TODO", "bug", "Bug confirmed")

    # Feature / enhancement with clear title
    if any(lb in {"feature", "feat", "feature request"} for lb in labels):
        if len(title) > 10:  # Has a real title
            return _result(number, title, labels, "TODO", "feature", "Feature with clear scope")

    # Recent issue with activity (< 14 days old AND updated recently)
    if age_days < 14 and last_update_days < 7:
        return _result(number, title, labels, "TODO", "recent-active", "New issue with recent activity")

    # ── BACKLOG bucket (everything else) ───────────────────────────
    reason = "backlog-default"
    reason_text = "No priority signal"

    if any(lb in BACKLOG_LABELS for lb in labels):
        reason = "backlog-label"
        reason_text = f"Label: {[l for l in labels if l in BACKLOG_LABELS]}"
    elif age_days > 30 and last_update_days > 30:
        reason = "stale"
        reason_text = f"Stale: {age_days}d old, {last_update_days}d since update"

    return _result(number, title, labels, "BACKLOG", reason, reason_text)


def _result(number, title, labels, bucket, reason_key, reason_text):
    return {
        "number": number,
        "title": title,
        "labels": labels,
        "bucket": bucket,
        "reason_key": reason_key,
        "reason_text": reason_text,
    }


# ─── PRIORITY SCORING (within bucket) ────────────────────────────────────────

def score_within_bucket(item: dict) -> float:
    """Score items within a bucket for ordering. Higher = more urgent."""
    labels = item.get("labels", [])
    score = 0.0

    # Label signals
    if "critical" in labels or "priority: critical" in labels:
        score += 30
    if "security" in labels:
        score += 25
    if "priority: high" in labels or "priority:high" in labels:
        score += 20
    if "bug" in labels:
        score += 10
    if "priority: medium" in labels:
        score += 5
    if "blocker" in labels:
        score += 15

    return score


# ─── SYSTEM-GENERATED ITEMS ──────────────────────────────────────────────────

def generate_system_items(
    docker: dict,
    tests: dict,
    visual: list,
) -> list[dict]:
    """
    Convert infrastructure failures and visual findings into triage items.
    These don't have GitHub issue numbers — they get synthetic IDs.
    """
    items = []
    synthetic_id = 90000  # High number to avoid collisions

    # Docker build failure → TASKS
    if docker.get("build_status") == "FAIL":
        items.append({
            "number": synthetic_id,
            "title": "[INFRA] Docker build failing",
            "labels": ["infra", "blocker"],
            "bucket": "TASKS",
            "reason_key": "docker-fail",
            "reason_text": "Docker build broken — blocks local dev and CI",
            "synthetic": True,
            "detail": docker.get("build_errors", []),
        })
        synthetic_id += 1

    # Failing tests → TASKS
    failing = tests.get("failing_tests", [])
    if tests.get("status") == "FAIL" and failing:
        for test_name in failing[:5]:  # Cap at 5
            items.append({
                "number": synthetic_id,
                "title": f"[TEST] Fix failing test: {test_name}",
                "labels": ["test", "blocker"],
                "bucket": "TASKS",
                "reason_key": "test-fail",
                "reason_text": f"Test failing in CI: {test_name}",
                "synthetic": True,
            })
            synthetic_id += 1
    elif tests.get("status") == "FAIL" and not failing:
        items.append({
            "number": synthetic_id,
            "title": "[TEST] Test suite failing",
            "labels": ["test", "blocker"],
            "bucket": "TASKS",
            "reason_key": "test-fail",
            "reason_text": "Test suite failing — see test-health.json for details",
            "synthetic": True,
        })
        synthetic_id += 1

    # Visual review findings
    for finding in visual:
        if finding.get("status") == "BROKEN":
            route = finding.get("route", "unknown")
            issues = finding.get("issues_found", [])
            bucket = "TASKS" if "/" in route and route in ["/", "/login", "/dashboard"] else "TODO"
            items.append({
                "number": synthetic_id,
                "title": f"[UI] Broken route: {route}",
                "labels": ["bug", "ui"],
                "bucket": bucket,
                "reason_key": "visual-broken",
                "reason_text": f"Visual review: {'; '.join(issues[:2])}",
                "synthetic": True,
                "detail": issues,
            })
            synthetic_id += 1

    return items


# ─── MARKDOWN WRITERS ─────────────────────────────────────────────────────────

def write_tasks_md(tasks: list[dict], docker: dict, tests: dict) -> str:
    today = now_str()
    build_status = docker.get("build_status", "SKIPPED")
    test_status = tests.get("status", "SKIPPED")
    test_summary = tests.get("summary", "")

    lines = [
        "# Tasks\n",
        "Priority work for the current sprint. Start here. Items feed directly into the engineering pipeline.\n",
        f"> Last updated: {today} by PO Lifecycle Orchestrator  ",
        f"> System health: Docker [{build_status}] · Tests [{test_status}]{' · ' + test_summary if test_summary else ''}\n",
        "---\n",
    ]

    # Group by priority within TASKS
    critical = [t for t in tasks if any(l in ["critical", "security", "blocker", "infra", "p0"] for l in t.get("labels", []))]
    high = [t for t in tasks if t not in critical and any(l in ["priority: high", "priority:high", "p1"] for l in t.get("labels", []))]
    other = [t for t in tasks if t not in critical and t not in high]

    if critical:
        lines.append("## 🔴 Critical / Blockers\n")
        for item in sorted(critical, key=score_within_bucket, reverse=True):
            lines.extend(_format_task_item(item))
        lines.append("")

    if high:
        lines.append("## 🟠 High Priority\n")
        for item in sorted(high, key=score_within_bucket, reverse=True):
            lines.extend(_format_task_item(item))
        lines.append("")

    if other:
        lines.append("## 🟡 This Sprint\n")
        for item in sorted(other, key=score_within_bucket, reverse=True):
            lines.extend(_format_task_item(item))
        lines.append("")

    if not tasks:
        lines.append("_No priority tasks. Check TODO.md for next items._\n")

    return "\n".join(lines)


def write_todo_md(todos: list[dict]) -> str:
    today = now_str()
    lines = [
        "# TODO\n",
        "Confirmed work for the next sprint. Items are validated and ready to assign once TASKS are cleared.\n",
        f"> Last updated: {today} by PO Lifecycle Orchestrator\n",
        "---\n",
    ]

    bugs = [t for t in todos if "bug" in t.get("labels", [])]
    features = [t for t in todos if any(l in ["feature", "feat", "feature request"] for l in t.get("labels", []))]
    refactors = [t for t in todos if any(l in ["refactor", "tech-debt"] for l in t.get("labels", []))]
    ui = [t for t in todos if "ui" in t.get("labels", [])]
    other = [t for t in todos if t not in bugs and t not in features and t not in refactors and t not in ui]

    sections = [
        ("## 🐛 Bugs", bugs),
        ("## ✨ Features", features),
        ("## 🎨 UI / Design", ui),
        ("## 🔧 Refactors", refactors),
        ("## 📋 Other", other),
    ]

    for header, items in sections:
        if items:
            lines.append(f"{header}\n")
            for item in sorted(items, key=score_within_bucket, reverse=True):
                lines.extend(_format_task_item(item))
            lines.append("")

    if not todos:
        lines.append("_No TODO items. Check BACKLOG.md to promote items._\n")

    return "\n".join(lines)


def write_backlog_md(backlog: list[dict]) -> str:
    today = now_str()
    lines = [
        "# Backlog\n",
        "Items requiring design, external decisions, or lower priority. Reviewed each sprint — graduate to TODO when ready.\n",
        f"> Last updated: {today} by PO Lifecycle Orchestrator\n",
        "---\n",
    ]

    enhancements = [t for t in backlog if any(l in ["enhancement", "idea", "feature request"] for l in t.get("labels", []))]
    tech_debt = [t for t in backlog if any(l in ["tech-debt", "refactor"] for l in t.get("labels", []))]
    needs_info = [t for t in backlog if any(l in ["question", "discussion", "design-needed", "needs-spec"] for l in t.get("labels", []))]
    stale = [t for t in backlog if t.get("reason_key") == "stale"]
    other = [t for t in backlog if t not in enhancements and t not in tech_debt and t not in needs_info and t not in stale]

    sections = [
        ("## 💡 Ideas & Enhancements", enhancements),
        ("## 🔩 Technical Debt", tech_debt),
        ("## ❓ Needs Discussion / Design", needs_info),
        ("## 💤 Stale (30+ days)", stale),
        ("## 📦 Other", other),
    ]

    for header, items in sections:
        if items:
            lines.append(f"{header}\n")
            for item in items:
                lines.extend(_format_backlog_item(item))
            lines.append("")

    if not backlog:
        lines.append("_Backlog is clean!_\n")

    return "\n".join(lines)


def _format_task_item(item: dict) -> list[str]:
    number = item.get("number", 0)
    title = item.get("title", "")
    labels = item.get("labels", [])
    reason = item.get("reason_text", "")
    is_synthetic = item.get("synthetic", False)

    label_str = " ".join(f"`{l}`" for l in labels[:4] if l not in ["triage:tasks", "triage:todo", "triage:backlog"])
    ref = f"(synthetic)" if is_synthetic else f"[#{number}](https://github.com/{{owner}}/{{repo}}/issues/{number})"

    lines = [f"- [ ] **{title}** {ref} {label_str}"]
    if item.get("detail"):
        detail = item["detail"]
        if isinstance(detail, list):
            for d in detail[:3]:
                lines.append(f"  - {d}")
        else:
            lines.append(f"  - {detail}")
    if reason:
        lines.append(f"  - _Reason: {reason}_")
    lines.append("")
    return lines


def _format_backlog_item(item: dict) -> list[str]:
    number = item.get("number", 0)
    title = item.get("title", "")
    labels = item.get("labels", [])
    reason = item.get("reason_text", "")
    is_synthetic = item.get("synthetic", False)

    label_str = " ".join(f"`{l}`" for l in labels[:3])
    ref = f"(synthetic)" if is_synthetic else f"[#{number}](https://github.com/{{owner}}/{{repo}}/issues/{number})"

    lines = [
        f"- [ ] **{title}** {ref} {label_str}",
        f"  - Status: Backlog — {reason}",
        "",
    ]
    return lines


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="PO triage engine")
    parser.add_argument("--issues",     required=True)
    parser.add_argument("--closed",     default=None)
    parser.add_argument("--prs",        default=None)
    parser.add_argument("--merged",     default=None)
    parser.add_argument("--docker",     default=None)
    parser.add_argument("--tests",      default=None)
    parser.add_argument("--visual",     default=None)
    parser.add_argument("--context",    default=None)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load inputs
    issues       = load_json(args.issues, [])
    closed       = load_json(args.closed, [])
    open_prs     = load_json(args.prs, [])
    merged_prs   = load_json(args.merged, [])
    docker       = load_json(args.docker, {"build_status": "SKIPPED"})
    tests        = load_json(args.tests, {"status": "SKIPPED"})
    visual_raw   = load_json(args.visual, [])
    visual       = visual_raw.get("findings", []) if isinstance(visual_raw, dict) else visual_raw

    print(f"Processing {len(issues)} open issues...")

    # Build reference sets
    closed_numbers = {i.get("number") for i in closed}
    merged_refs = get_merged_issue_refs(merged_prs)
    in_flight = get_in_flight_issues(open_prs)

    print(f"  Merged PR issue refs: {len(merged_refs)}")
    print(f"  In-flight (open PR) issue refs: {len(in_flight)}")

    # Triage all issues
    matrix = []
    for issue in issues:
        result = triage_issue(
            issue, closed_numbers, merged_refs, in_flight,
            docker.get("build_status", "SKIPPED"),
            tests.get("status", "SKIPPED"),
        )
        matrix.append(result)

    # Add system-generated items (docker/test/visual failures)
    system_items = generate_system_items(docker, tests, visual)
    matrix.extend(system_items)

    # Split into buckets
    tasks_items   = sorted([m for m in matrix if m["bucket"] == "TASKS"],   key=score_within_bucket, reverse=True)
    todo_items    = sorted([m for m in matrix if m["bucket"] == "TODO"],     key=score_within_bucket, reverse=True)
    backlog_items = [m for m in matrix if m["bucket"] == "BACKLOG"]
    skipped_items = [m for m in matrix if m["bucket"] == "SKIP"]

    # Save matrix
    with open(output_dir / "triage-matrix.json", "w") as f:
        json.dump(matrix, f, indent=2)

    # Write planning files to repo root
    tasks_md   = write_tasks_md(tasks_items, docker, tests)
    todo_md    = write_todo_md(todo_items)
    backlog_md = write_backlog_md(backlog_items)

    Path("TASKS.md").write_text(tasks_md)
    Path("TODO.md").write_text(todo_md)
    Path("BACKLOG.md").write_text(backlog_md)

    # Summary
    print(f"\n{'─' * 56}")
    print(f"  📋 TRIAGE COMPLETE — {now_str()}")
    print(f"{'─' * 56}")
    print(f"  🔴 TASKS.md    → {len(tasks_items)} items")
    print(f"  🟡 TODO.md     → {len(todo_items)} items")
    print(f"  🔵 BACKLOG.md  → {len(backlog_items)} items")
    print(f"  ✅ Skipped      → {len(skipped_items)} items")
    print(f"{'─' * 56}")

    if tasks_items:
        top = tasks_items[0]
        print(f"\n  🎯 Top priority:")
        print(f"     #{top['number']} — {top['title']}")
        print(f"     Reason: {top['reason_text']}")

    print(f"\n  Files written:")
    print(f"    TASKS.md ({len(tasks_items)} items)")
    print(f"    TODO.md ({len(todo_items)} items)")
    print(f"    BACKLOG.md ({len(backlog_items)} items)")
    print(f"    {output_dir}/triage-matrix.json")


if __name__ == "__main__":
    main()
