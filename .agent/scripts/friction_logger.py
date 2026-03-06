#!/usr/bin/env python3
"""Append structured friction events to .agent/logs/FRICTION.md."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRICTION_LOG = ROOT / ".agent" / "logs" / "FRICTION.md"


def _sanitize(value: str) -> str:
    return " ".join(value.strip().split())


def append_entry(task: str, event_type: str, friction: str, resolution: str) -> None:
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    entry = (
        f"\n### [{date_str}] {task}\n"
        f"- **Type**: {event_type}\n"
        f"- **Friction**: {friction}\n"
        f"- **Resolution**: {resolution}\n"
        f"- **Action Required**: Review and codify prevention in workflows/rules.\n"
    )
    FRICTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with FRICTION_LOG.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a friction event")
    parser.add_argument("--task", required=True, help="Workflow/task name")
    parser.add_argument("--type", required=True, help="Friction type")
    parser.add_argument("--friction", required=True, help="What failed")
    parser.add_argument("--resolution", required=True, help="Current mitigation")
    args = parser.parse_args()

    append_entry(
        task=_sanitize(args.task),
        event_type=_sanitize(args.type),
        friction=_sanitize(args.friction),
        resolution=_sanitize(args.resolution),
    )
    print(f"Friction logged to {FRICTION_LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
