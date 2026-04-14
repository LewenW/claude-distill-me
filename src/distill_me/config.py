"""Paths and constants."""

import os
from pathlib import Path

CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_HOME / "projects"
SHARED_MEMORY_DIR = CLAUDE_HOME / "shared-memory"
GLOBAL_CLAUDE_MD = CLAUDE_HOME / "CLAUDE.md"

# Patterns persist under ~/.claude so they survive reinstalls
OUTPUT_DIR = CLAUDE_HOME / "distill-me"
PATTERNS_DIR = OUTPUT_DIR / "patterns"

# Plugin assets: CLAUDE_PLUGIN_ROOT (set by plugin loader) > source tree > bundled in package
_plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
if _plugin_root_env:
    PLUGIN_ROOT = Path(_plugin_root_env)
else:
    # Works for both `pip install -e .` (source tree) and `pip install .` (site-packages)
    _source_root = Path(__file__).resolve().parent.parent.parent
    _has_assets = (_source_root / "references").is_dir()
    PLUGIN_ROOT = _source_root if _has_assets else Path(__file__).resolve().parent

ENHANCED_SKILL_DIR = PLUGIN_ROOT / "skills" / "enhanced-self"
ROLE_TEMPLATES_DIR = PLUGIN_ROOT / "references" / "role-templates"

SCAN_DAYS = 30
MAX_SESSIONS = 20
MAX_TURNS_PER_SESSION = 50
MAX_TOTAL_TURNS = 100
MAX_MESSAGE_CHARS = 2000

_exclude_raw = os.environ.get("DISTILLME_EXCLUDE_PROJECTS", "")
EXCLUDE_PROJECTS: set[str] = {
    p.strip() for p in _exclude_raw.split(",") if p.strip()
}

# Markers for injecting generated content into ~/.claude/CLAUDE.md
CLAUDE_MD_START = "<!-- distill-me:start -->"
CLAUDE_MD_END = "<!-- distill-me:end -->"
