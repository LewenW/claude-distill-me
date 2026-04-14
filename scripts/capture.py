#!/usr/bin/env python3
"""UserPromptSubmit hook: detect and queue learning signals from each user message."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from plus_me.queue import detect_learning, append_learning


def main() -> int:
    input_data = sys.stdin.read()
    if not input_data:
        return 0

    try:
        data = json.loads(input_data)
    except json.JSONDecodeError:
        return 0

    prompt = data.get("prompt") or data.get("message") or data.get("text")
    if not prompt:
        return 0

    learning = detect_learning(prompt)
    if not learning:
        return 0

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    append_learning(learning, project_dir)

    preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
    print(f"[plus-me] captured: '{preview}' ({learning.learning_type}, {learning.confidence:.0%})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
