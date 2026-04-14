#!/usr/bin/env python3
"""Stop hook: summarize learnings captured during this session."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from plus_me.queue import queue_stats


def main() -> int:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    stats = queue_stats(project_dir)

    if stats["total"] == 0:
        return 0

    by_type = stats["by_type"]
    parts = [f"{v} {k}" for k, v in sorted(by_type.items())]
    summary = ", ".join(parts)

    print(
        f"[plus-me] {stats['total']} learnings queued ({summary}). "
        f"Run /plus-me:distill to synthesize into your personal skill."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
