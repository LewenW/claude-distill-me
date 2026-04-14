#!/usr/bin/env python3
"""Stop hook: summarize learnings captured during this session."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from distill_me.queue import prune_stale, queue_stats


def main() -> int:
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    pruned = prune_stale(project_dir)
    stats = queue_stats(project_dir)

    if stats["total"] == 0:
        return 0

    by_type = stats["by_type"]
    parts = [f"{v} {k}" for k, v in sorted(by_type.items())]
    summary = ", ".join(parts)

    msg = f"[distill-me] {stats['total']} learnings queued ({summary})."
    if pruned:
        msg += f" ({pruned} stale items pruned.)"
    if stats["total"] >= 10:
        msg += " Run /distill-me:distill to synthesize."
    print(msg, file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
