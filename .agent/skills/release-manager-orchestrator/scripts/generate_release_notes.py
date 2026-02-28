#!/usr/bin/env python3
"""
Classify commits since last tag and generate release notes in two formats.

Usage:
  python3 generate_release_notes.py \
    --commits <path-to-commits-since-tag.txt> \
    --current-version 1.3.0 \
    --output-dir .agent/tmp/
"""

import argparse
import json
import re
from datetime import date
from pathlib import Path


CATEGORY_CONFIG = {
    "feat":     ("added",       "✨ Added",       "MINOR"),
    "fix":      ("fixed",       "🐛 Fixed",       "PATCH"),
    "perf":     ("performance", "⚡ Performance",  "PATCH"),
    "security": ("security",    "🔒 Security",     "PATCH"),
    "refactor": ("changed",     "🔧 Changed",      "PATCH"),
    "revert":   ("changed",     "↩ Reverted",     "PATCH"),
    "docs":     ("maintenance", "📚 Docs",         None),
    "chore":    ("maintenance", "🔩 Maintenance",  None),
    "ci":       ("maintenance", "🔩 Maintenance",  None),
    "test":     ("maintenance", "🔩 Maintenance",  None),
    "build":    ("maintenance", "🔩 Maintenance",  None),
    "style":    ("maintenance", "🔩 Maintenance",  None),
}

SEMVER_RANK = {"MAJOR": 3, "MINOR": 2, "PATCH": 1, None: 0}


def parse_commits(commits_file: Path) -> list[dict]:
    """Parse lines from `git log --oneline --no-merges` output."""
    commits = []
    with open(commits_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Format: <sha> <subject>
            parts = line.split(" ", 1)
            sha = parts[0]
            subject = parts[1] if len(parts) > 1 else ""
            commits.append({"sha": sha[:8], "subject": subject})
    return commits


def classify_commit(commit: dict) -> tuple[str, str, str | None, bool]:
    """
    Returns: (category_key, formatted_description, semver_impact, is_breaking)
    """
    subject = commit["subject"]
    is_breaking = False

    # Detect breaking change marker
    if "BREAKING CHANGE" in subject or "!:" in subject or subject.endswith("!"):
        is_breaking = True

    # Try conventional commit pattern: type(scope)!: description
    match = re.match(r"^(\w+)(?:\(([^)]+)\))?!?:\s*(.+)$", subject)
    if match:
        commit_type = match.group(1).lower()
        scope = match.group(2)
        description = match.group(3)

        config = CATEGORY_CONFIG.get(commit_type)
        if config:
            category_key, _, semver_impact = config
            formatted = f"{scope + ': ' if scope else ''}{description} (`{commit['sha']}`)"
            return category_key, formatted, semver_impact, is_breaking

    # No conventional prefix — best-effort classification
    subject_lower = subject.lower()
    if any(w in subject_lower for w in ["fix", "bug", "error", "crash", "patch", "resolve"]):
        return "fixed", f"{subject} (`{commit['sha']}`)", "PATCH", is_breaking
    if any(w in subject_lower for w in ["add", "feat", "implement", "create", "new", "support", "introduce"]):
        return "added", f"{subject} (`{commit['sha']}`)", "MINOR", is_breaking
    if any(w in subject_lower for w in ["security", "cve", "vuln", "xss", "injection"]):
        return "security", f"{subject} (`{commit['sha']}`)", "PATCH", is_breaking
    if any(w in subject_lower for w in ["perf", "speed", "optim", "faster", "slow"]):
        return "performance", f"{subject} (`{commit['sha']}`)", "PATCH", is_breaking

    return "maintenance", f"{subject} (`{commit['sha']}`)", None, is_breaking


def group_commits(commits: list[dict]) -> dict:
    groups: dict[str, list[str]] = {
        "breaking":    [],
        "added":       [],
        "fixed":       [],
        "security":    [],
        "performance": [],
        "changed":     [],
        "maintenance": [],
    }
    highest_impact = None

    for commit in commits:
        category, description, semver_impact, is_breaking = classify_commit(commit)

        if is_breaking:
            groups["breaking"].append(description)
            # Breaking always means MAJOR
            highest_impact = "MAJOR"
        else:
            if SEMVER_RANK.get(semver_impact, 0) > SEMVER_RANK.get(highest_impact, 0):
                highest_impact = semver_impact

        groups[category].append(description)

    return groups, highest_impact or "PATCH"


def compute_next_version(current: str, bump: str) -> str:
    """Parse X.Y.Z and apply bump."""
    current = current.lstrip("v")
    parts = current.split(".")
    if len(parts) != 3:
        # Fallback
        return "0.1.0" if bump == "MINOR" else "1.0.0" if bump == "MAJOR" else "0.0.1"

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump == "MAJOR":
        return f"{major + 1}.0.0"
    elif bump == "MINOR":
        return f"{major}.{minor + 1}.0"
    else:  # PATCH
        return f"{major}.{minor}.{patch + 1}"


def build_reason(groups: dict, bump: str) -> str:
    counts = []
    if groups.get("breaking"):
        counts.append(f"{len(groups['breaking'])} breaking change(s)")
    if groups.get("added"):
        counts.append(f"{len(groups['added'])} feature(s)")
    if groups.get("fixed"):
        counts.append(f"{len(groups['fixed'])} fix(es)")
    if groups.get("security"):
        counts.append(f"{len(groups['security'])} security fix(es)")
    return f"{bump} — {', '.join(counts)}" if counts else bump


def format_changelog_entry(version: str, groups: dict) -> str:
    today = date.today().isoformat()
    lines = [f"## [{version}] — {today}\n"]

    if groups.get("breaking"):
        lines.append("### ⚠️ BREAKING CHANGES\n")
        for item in groups["breaking"]:
            lines.append(f"- {item}")
        lines.append("")

    section_order = [
        ("added",       "### ✨ Added"),
        ("fixed",       "### 🐛 Fixed"),
        ("security",    "### 🔒 Security"),
        ("performance", "### ⚡ Performance"),
        ("changed",     "### 🔧 Changed"),
    ]

    for key, header in section_order:
        items = groups.get(key, [])
        # Exclude items already listed as breaking
        breaking_set = set(groups.get("breaking", []))
        items = [i for i in items if i not in breaking_set]
        if items:
            lines.append(f"{header}\n")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")

    maintenance = groups.get("maintenance", [])
    if maintenance:
        lines.append("<details>")
        lines.append("<summary>🔩 Internal / Maintenance</summary>\n")
        for item in maintenance:
            lines.append(f"- {item}")
        lines.append("</details>\n")

    return "\n".join(lines)


def format_release_body(version: str, groups: dict, current_version: str) -> str:
    lines = [f"## What's new in v{version}\n"]

    breaking = groups.get("breaking", [])
    added = groups.get("added", [])
    fixed = groups.get("fixed", [])
    security = groups.get("security", [])

    if breaking:
        lines.append(f"> ⚠️ **This release contains {len(breaking)} breaking change(s).** See the Upgrading section below.\n")

    if added:
        lines.append("### ✨ Highlights\n")
        for item in added[:6]:  # Top 6
            lines.append(f"- {item}")
        lines.append("")

    if fixed:
        lines.append("### 🐛 Bug Fixes\n")
        for item in fixed[:8]:
            lines.append(f"- {item}")
        lines.append("")

    if security:
        lines.append("### 🔒 Security\n")
        for item in security:
            lines.append(f"- {item}")
        lines.append("")

    if breaking:
        lines.append("### Upgrading from v{current_version}\n")
        lines.append("The following breaking changes require action:\n")
        for item in breaking:
            lines.append(f"- {item}")
        lines.append("")

    lines.append(f"**Full changelog:** https://github.com/{{owner}}/{{repo}}/compare/v{current_version}...v{version}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate release notes from commits")
    parser.add_argument("--commits", required=True, help="Path to commits-since-tag.txt")
    parser.add_argument("--current-version", required=True, help="Current version (e.g. 1.3.0)")
    parser.add_argument("--output-dir", required=True, help="Directory for output files")
    args = parser.parse_args()

    commits_path = Path(args.commits)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    commits = parse_commits(commits_path)
    print(f"Processing {len(commits)} commit(s)...")

    groups, bump = group_commits(commits)
    next_version = compute_next_version(args.current_version, bump)
    reason = build_reason(groups, bump)

    # Write commit map
    commit_map = {k: v for k, v in groups.items() if v}
    with open(output_dir / "commit-map.json", "w") as f:
        json.dump(commit_map, f, indent=2)

    # Write SemVer recommendation
    semver_rec = {
        "bump": bump,
        "current_version": args.current_version.lstrip("v"),
        "next_version": next_version,
        "reason": reason,
    }
    with open(output_dir / "semver-recommendation.json", "w") as f:
        json.dump(semver_rec, f, indent=2)

    # Write CHANGELOG entry
    changelog_entry = format_changelog_entry(next_version, groups)
    with open(output_dir / "changelog-entry.md", "w") as f:
        f.write(changelog_entry)

    # Write release body
    release_body = format_release_body(next_version, groups, args.current_version.lstrip("v"))
    with open(output_dir / "release-body.md", "w") as f:
        f.write(release_body)

    print(f"\n{'─' * 48}")
    print(f"  Current:     v{args.current_version.lstrip('v')}")
    print(f"  Suggested:   v{next_version}  [{reason}]")
    print(f"{'─' * 48}")
    print(f"\n✅ Files written to {output_dir}/")
    print(f"   commit-map.json")
    print(f"   semver-recommendation.json")
    print(f"   changelog-entry.md")
    print(f"   release-body.md")


if __name__ == "__main__":
    main()
