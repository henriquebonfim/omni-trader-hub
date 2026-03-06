#!/usr/bin/env python3
"""SOP enforcement gate for .agent workflows.

Run before each workflow to validate mandatory preconditions.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
STACK_MAKE = ROOT / ".agent" / "scripts" / "make" / "stack.make"
GITIGNORE = ROOT / ".gitignore"


@dataclass
class Rule:
    name: str
    severity: str  # CRITICAL or HIGH
    check: Callable[[], tuple[bool, str]]


def _current_branch() -> str:
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def check_not_protected_branch() -> tuple[bool, str]:
    protected = {"main", "master", "production", "staging"}
    branch = _current_branch()
    if not branch:
        return False, "Cannot determine current git branch"
    if branch in protected:
        return False, f"Protected branch detected: {branch}"
    return True, f"Branch OK: {branch}"


def check_release_branch() -> tuple[bool, str]:
    allowed = {"main", "master"}
    branch = _current_branch()
    if not branch:
        return False, "Cannot determine current git branch"
    if branch not in allowed:
        return False, f"Release must run on main/master. Current: {branch}"
    return True, f"Release branch OK: {branch}"


def check_docker_available() -> tuple[bool, str]:
    result = subprocess.run(
        ["docker", "compose", "version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False, "docker compose is not available"
    return True, "docker compose available"


def check_makefile_targets() -> tuple[bool, str]:
    required = {"build", "test", "lint", "typecheck"}
    if not STACK_MAKE.exists():
        return False, f"Missing file: {STACK_MAKE.relative_to(ROOT)}"
    content = STACK_MAKE.read_text(encoding="utf-8")
    found = {
        line.split(":", 1)[0].strip() for line in content.splitlines() if ":" in line
    }
    missing = sorted(required - found)
    if missing:
        return False, f"Missing make targets in stack.make: {', '.join(missing)}"
    return True, "Required make targets found"


def check_tmp_gitignore() -> tuple[bool, str]:
    if not GITIGNORE.exists():
        return False, "Missing .gitignore"
    entries = GITIGNORE.read_text(encoding="utf-8").splitlines()
    if ".agent/tmp/" not in entries:
        return False, "Missing .agent/tmp/ entry in .gitignore"
    return True, ".agent/tmp/ ignored"


def check_sequential_token() -> tuple[bool, str]:
    token = os.environ.get("THINKING_SESSION_ID")
    if not token:
        # Keep this as HIGH so teams can enforce progressively without breaking flows.
        return False, "THINKING_SESSION_ID is not set"
    return True, "Sequential-thinking token present"


WORKFLOW_RULES: dict[str, list[Rule]] = {
    "start-workflow": [
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-issues": [
        Rule("branch-safety", "CRITICAL", check_not_protected_branch),
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-code": [
        Rule("branch-safety", "CRITICAL", check_not_protected_branch),
        Rule("sequential-thinking", "HIGH", check_sequential_token),
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
    ],
    "handle-po-review": [
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-backlog-triage": [
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-pr-review": [
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-pr-code": [
        Rule("branch-safety", "CRITICAL", check_not_protected_branch),
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-close-pr": [
        Rule("tmp-gitignore", "CRITICAL", check_tmp_gitignore),
    ],
    "handle-release": [
        Rule("release-branch", "CRITICAL", check_release_branch),
        Rule("docker-first", "HIGH", check_docker_available),
        Rule("makefile-targets", "CRITICAL", check_makefile_targets),
    ],
}


def run(workflow: str) -> int:
    rules = WORKFLOW_RULES.get(workflow)
    if not rules:
        known = ", ".join(sorted(WORKFLOW_RULES.keys()))
        print(f"ERROR Unknown workflow '{workflow}'. Known: {known}")
        return 2

    print(f"SOP validation: {workflow}")
    failures = 0
    warnings = 0

    for rule in rules:
        ok, message = rule.check()
        if ok:
            print(f"PASS [{rule.severity}] {rule.name}: {message}")
            continue
        if rule.severity == "CRITICAL":
            failures += 1
            print(f"FAIL [CRITICAL] {rule.name}: {message}")
        else:
            warnings += 1
            print(f"WARN [HIGH] {rule.name}: {message}")

    if failures:
        print(f"Validation failed with {failures} critical issue(s)")
        return 1

    if warnings:
        print(f"Validation passed with {warnings} warning(s)")
    else:
        print("Validation passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SOP preconditions for workflow execution"
    )
    parser.add_argument("workflow", help="Workflow key (e.g. handle-code)")
    args = parser.parse_args()
    return run(args.workflow)


if __name__ == "__main__":
    raise SystemExit(main())
