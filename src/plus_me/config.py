"""Path configuration and constants for Plus-Me."""

import os
from pathlib import Path

CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_HOME / "projects"
SHARED_MEMORY_DIR = CLAUDE_HOME / "shared-memory"
GLOBAL_CLAUDE_MD = CLAUDE_HOME / "CLAUDE.md"

# Plugin root: resolved at runtime from env or relative to this file
PLUGIN_ROOT = Path(os.environ.get(
    "CLAUDE_PLUGIN_ROOT",
    Path(__file__).resolve().parent.parent.parent,
))
OUTPUT_DIR = PLUGIN_ROOT / "output"
PATTERNS_DIR = OUTPUT_DIR / "patterns"
ENHANCED_SKILL_DIR = PLUGIN_ROOT / "skills" / "enhanced-self"
ROLE_TEMPLATES_DIR = PLUGIN_ROOT / "references" / "role-templates"

# Scanner limits
MAX_SESSIONS = 10
MAX_TURNS_PER_SESSION = 100
MAX_TOTAL_TURNS = 500
MAX_MESSAGE_CHARS = 2000  # truncate long messages for analysis
