"""Generate personal SKILL.md from extracted patterns + optional role fusion."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from distill_me.config import (
    CLAUDE_MD_END,
    CLAUDE_MD_START,
    ENHANCED_SKILL_DIR,
    GLOBAL_CLAUDE_MD,
    PATTERNS_DIR,
    PLUGINS_DIR,
    ROLE_TEMPLATES_DIR,
)


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def _scan_plugin_skills() -> dict[str, Path]:
    """Scan installed Cowork plugins for SKILL.md files usable as role templates.

    Returns {display_name: skill_path} for each found skill.
    Skips distill-me's own skills.
    """
    if not PLUGINS_DIR.is_dir():
        return {}

    skills: dict[str, Path] = {}
    for plugin_dir in PLUGINS_DIR.iterdir():
        if not plugin_dir.is_dir():
            continue
        if plugin_dir.name == "distill-me":
            continue
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue
        for skill_dir in skills_dir.iterdir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.is_file():
                name = f"{plugin_dir.name}/{skill_dir.name}"
                skills[name] = skill_file

    return skills


def load_role_template(role: str) -> str | None:
    """Load a role template. Checks built-in templates first, then installed plugins."""
    # Built-in templates
    path = ROLE_TEMPLATES_DIR / f"{role}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")

    # Installed plugin skills (match by plugin name or full plugin/skill name)
    plugin_skills = _scan_plugin_skills()
    for name, skill_path in plugin_skills.items():
        if role == name or role == name.split("/")[0]:
            return skill_path.read_text(encoding="utf-8")

    return None


def available_roles() -> list[str]:
    """List all available roles: built-in templates + installed plugin skills."""
    roles: list[str] = []

    if ROLE_TEMPLATES_DIR.is_dir():
        roles.extend(f.stem for f in ROLE_TEMPLATES_DIR.glob("*.md"))

    plugin_skills = _scan_plugin_skills()
    roles.extend(plugin_skills.keys())

    return roles


def _backup_patterns() -> Path | None:
    if not PATTERNS_DIR.exists():
        return None
    existing = list(PATTERNS_DIR.glob("*.md"))
    if not existing:
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup_dir = PATTERNS_DIR.parent / "patterns-backups" / ts
    _ensure_dir(backup_dir)
    import shutil
    for f in existing:
        shutil.copy2(f, backup_dir / f.name)
    return backup_dir


def save_patterns(judgment: str, style: str, priorities: str) -> dict:
    """Save extracted patterns. Backs up existing patterns first."""
    backup = _backup_patterns()
    _ensure_dir(PATTERNS_DIR)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    files = {
        "judgment.md": (
            f"---\nname: Judgment Patterns\ndescription: Decision-making and cognitive patterns\n"
            f"type: judgment\nupdated: {now}\n---\n\n{judgment}"
        ),
        "style.md": (
            f"---\nname: Communication Style\ndescription: Voice, personality, and communication patterns\n"
            f"type: style\nupdated: {now}\n---\n\n{style}"
        ),
        "priorities.md": (
            f"---\nname: Work Priorities\ndescription: Values hierarchy and work philosophy\n"
            f"type: priorities\nupdated: {now}\n---\n\n{priorities}"
        ),
    }

    saved = {}
    for fname, content in files.items():
        path = PATTERNS_DIR / fname
        path.write_text(content, encoding="utf-8")
        saved[fname] = str(path)

    if backup:
        saved["_backup"] = str(backup)
    return saved


def read_patterns() -> dict[str, str] | None:
    if not PATTERNS_DIR.exists():
        return None

    result = {}
    for name in ("judgment", "style", "priorities"):
        path = PATTERNS_DIR / f"{name}.md"
        if path.exists():
            result[name] = path.read_text(encoding="utf-8")

    return result if result else None


def generate_skill(
    judgment: str,
    style: str,
    priorities: str,
    role: str | None = None,
    custom_instructions: str | None = None,
) -> str:
    """Generate a personal SKILL.md from patterns and optional role template."""
    role_section = ""
    if role:
        template = load_role_template(role)
        if template:
            display = role.upper().replace("/", " / ")
            role_section = (
                f"\n## Role Enhancement: {display}\n\n"
                f"Apply these best practices, filtered through the user's "
                f"personal style above. Personal patterns take priority — "
                f"adapt the practices to fit the person, not the reverse.\n\n"
                f"{template}\n"
            )

    custom_section = ""
    if custom_instructions:
        custom_section = f"\n## Additional Instructions\n\n{custom_instructions}\n"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return f"""---
name: enhanced-self
description: Deep behavioral patterns — decision-making, cognitive habits, communication style, values. Use when acting on behalf of this user.
when_to_use: When drafting, coding, deciding, reviewing, or doing any task as/for this user. Match their thinking, not just their preferences.
---

# Your User's Behavioral DNA

Generated by Distill-Me on {now}. These patterns go beyond preferences — \
they capture how this user thinks, decides, and communicates. When acting \
on their behalf, embody these patterns. Output should feel like it came \
from them.

## Decision-Making & Cognitive Patterns

{judgment}

## Communication & Personality

{style}

## Values & Work Philosophy

{priorities}
{role_section}{custom_section}"""


def save_skill(skill_content: str) -> str:
    _ensure_dir(ENHANCED_SKILL_DIR)
    path = ENHANCED_SKILL_DIR / "SKILL.md"
    path.write_text(skill_content, encoding="utf-8")
    return str(path)


def _backup_claude_md() -> Path | None:
    if not GLOBAL_CLAUDE_MD.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    backup = GLOBAL_CLAUDE_MD.with_name(f"CLAUDE.md.{ts}.bak")
    import shutil
    shutil.copy2(GLOBAL_CLAUDE_MD, backup)
    return backup


def inject_into_claude_md(skill_content: str) -> str:
    """Inject generated skill into ~/.claude/CLAUDE.md between markers.

    Backs up existing file first. Creates the file if it doesn't exist.
    Updates the marked section if it already exists. Preserves all other content.
    """
    _backup_claude_md()
    stripped = strip_frontmatter(skill_content)
    injection = f"{CLAUDE_MD_START}\n{stripped}\n{CLAUDE_MD_END}"

    if GLOBAL_CLAUDE_MD.exists():
        existing = GLOBAL_CLAUDE_MD.read_text(encoding="utf-8")
        start_idx = existing.find(CLAUDE_MD_START)
        end_idx = existing.find(CLAUDE_MD_END)

        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            new_content = (
                existing[:start_idx]
                + injection
                + existing[end_idx + len(CLAUDE_MD_END):]
            )
        else:
            new_content = existing.rstrip() + "\n\n" + injection + "\n"
    else:
        GLOBAL_CLAUDE_MD.parent.mkdir(parents=True, exist_ok=True)
        new_content = injection + "\n"

    GLOBAL_CLAUDE_MD.write_text(new_content, encoding="utf-8")
    return str(GLOBAL_CLAUDE_MD)
