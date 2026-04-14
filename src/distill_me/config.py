"""Paths and constants."""

import os
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    val = os.environ.get(name, "")
    try:
        return int(val) if val else default
    except ValueError:
        return default


CLAUDE_HOME = Path(os.environ.get("CLAUDE_HOME", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_HOME / "projects"
SHARED_MEMORY_DIR = CLAUDE_HOME / "shared-memory"
GLOBAL_CLAUDE_MD = CLAUDE_HOME / "CLAUDE.md"
PLUGINS_DIR = CLAUDE_HOME / "plugins"

# Patterns persist under ~/.claude so they survive reinstalls
OUTPUT_DIR = CLAUDE_HOME / "distill-me"
PATTERNS_DIR = OUTPUT_DIR / "patterns"

# Plugin assets: CLAUDE_PLUGIN_ROOT (set by plugin loader) > source tree > bundled in package
_plugin_root_env = os.environ.get("CLAUDE_PLUGIN_ROOT")
if _plugin_root_env:
    PLUGIN_ROOT = Path(_plugin_root_env)
else:
    _source_root = Path(__file__).resolve().parent.parent.parent
    _has_assets = (_source_root / "references").is_dir()
    PLUGIN_ROOT = _source_root if _has_assets else Path(__file__).resolve().parent

ENHANCED_SKILL_DIR = PLUGIN_ROOT / "skills" / "enhanced-self"
ROLE_TEMPLATES_DIR = PLUGIN_ROOT / "references" / "role-templates"

# All limits configurable via DISTILLME_* env vars
SCAN_DAYS = _int_env("DISTILLME_SCAN_DAYS", 30)
MAX_SESSIONS = _int_env("DISTILLME_MAX_SESSIONS", 20)
MAX_TURNS_PER_SESSION = _int_env("DISTILLME_MAX_TURNS_PER_SESSION", 50)
MAX_TOTAL_TURNS = _int_env("DISTILLME_MAX_TOTAL_TURNS", 100)
MAX_MESSAGE_CHARS = _int_env("DISTILLME_MAX_MESSAGE_CHARS", 2000)
MAX_MEMORY_CHARS = _int_env("DISTILLME_MAX_MEMORY_CHARS", 1000)
MAX_ANALYSIS_TURNS = _int_env("DISTILLME_MAX_ANALYSIS_TURNS", 80)

_exclude_raw = os.environ.get("DISTILLME_EXCLUDE_PROJECTS", "")
EXCLUDE_PROJECTS: set[str] = {
    p.strip() for p in _exclude_raw.split(",") if p.strip()
}

# Markers for injecting generated content into ~/.claude/CLAUDE.md
CLAUDE_MD_START = "<!-- distill-me:start -->"
CLAUDE_MD_END = "<!-- distill-me:end -->"
