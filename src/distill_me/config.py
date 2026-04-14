"""Paths and constants."""

import os
from pathlib import Path

CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_HOME / "projects"
SHARED_MEMORY_DIR = CLAUDE_HOME / "shared-memory"
GLOBAL_CLAUDE_MD = CLAUDE_HOME / "CLAUDE.md"

PLUGIN_ROOT = Path(os.environ.get(
    "CLAUDE_PLUGIN_ROOT",
    Path(__file__).resolve().parent.parent.parent,
))
OUTPUT_DIR = PLUGIN_ROOT / "output"
PATTERNS_DIR = OUTPUT_DIR / "patterns"
ENHANCED_SKILL_DIR = PLUGIN_ROOT / "skills" / "enhanced-self"
ROLE_TEMPLATES_DIR = PLUGIN_ROOT / "references" / "role-templates"
PLUGINS_DIR = CLAUDE_HOME / "plugins"
EXPORT_DIR = PLUGIN_ROOT / "import"

SCAN_DAYS = 30
MAX_SESSIONS = 20
MAX_TURNS_PER_SESSION = 50
MAX_TOTAL_TURNS = 500
MAX_MESSAGE_CHARS = 2000

# Projects to exclude from scanning (privacy). Matches against encoded dir names.
# Users can set via env: DISTILLME_EXCLUDE_PROJECTS="medical-app,diary"
_exclude_raw = os.environ.get("DISTILLME_EXCLUDE_PROJECTS", "")
EXCLUDE_PROJECTS: set[str] = {
    p.strip() for p in _exclude_raw.split(",") if p.strip()
}
