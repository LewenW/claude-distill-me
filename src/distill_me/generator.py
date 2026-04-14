"""Generate personal SKILL.md from extracted patterns + installed skills."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from distill_me.config import ENHANCED_SKILL_DIR, PATTERNS_DIR, PLUGINS_DIR, ROLE_TEMPLATES_DIR


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def scan_installed_skills() -> dict[str, Path]:
    """Find all installed Cowork plugin skills. Returns {name: path}.

    Disambiguates duplicate names by prefixing with the parent plugin
    directory (e.g. "plugin-a/access" vs "plugin-b/access").
    """
    raw: list[tuple[str, Path]] = []
    if not PLUGINS_DIR.exists():
        return {}
    for skill_md in PLUGINS_DIR.rglob("SKILL.md"):
        try:
            first_lines = skill_md.read_text(encoding="utf-8")[:500]
            for line in first_lines.splitlines():
                if line.startswith("name:"):
                    name = line.partition(":")[2].strip()
                    if name:
                        raw.append((name, skill_md))
                    break
        except OSError:
            continue

    # Detect duplicates and disambiguate with plugin name prefix
    seen: dict[str, int] = {}
    for name, _ in raw:
        seen[name] = seen.get(name, 0) + 1

    results: dict[str, Path] = {}
    for name, path in raw:
        if seen[name] > 1:
            # Walk up from SKILL.md to find the plugin directory name
            # e.g. .../external_plugins/discord/skills/access/SKILL.md → "discord"
            plugin_name = _find_plugin_name(path)
            key = f"{plugin_name}/{name}"
        else:
            key = name
        results[key] = path
    return results


def _find_plugin_name(skill_path: Path) -> str:
    """Extract the plugin directory name from a SKILL.md path.

    Walks up looking for a 'skills' directory, then goes one level above it.
    """
    for parent in skill_path.parents:
        if parent.name == "skills" and parent.parent.name != "":
            return parent.parent.name
    return skill_path.parent.name


def load_role_template(role: str) -> str | None:
    """Load a role template by name — checks built-in templates first,
    then installed Cowork skills. Returns None if ambiguous (multiple matches)."""
    path = ROLE_TEMPLATES_DIR / f"{role}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")

    installed = scan_installed_skills()
    # Exact match first
    if role in installed:
        content = installed[role].read_text(encoding="utf-8")
        return _strip_frontmatter(content)
    # Fuzzy match — only if exactly one hit
    matches = [(n, p) for n, p in installed.items() if role.lower() in n.lower()]
    if len(matches) == 1:
        content = matches[0][1].read_text(encoding="utf-8")
        return _strip_frontmatter(content)
    return None


def available_roles() -> list[str]:
    """List available role templates + installed Cowork skills."""
    roles = []
    if ROLE_TEMPLATES_DIR.exists():
        roles.extend(f.stem for f in ROLE_TEMPLATES_DIR.glob("*.md"))

    installed = scan_installed_skills()
    roles.extend(sorted(installed.keys()))
    return roles


def _backup_patterns() -> Path | None:
    """Copy existing patterns to a timestamped backup dir. Returns backup path."""
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
    """Save extracted patterns to output/patterns/ directory.

    Backs up existing patterns before overwriting.
    """
    backup = _backup_patterns()
    _ensure_dir(PATTERNS_DIR)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    files = {
        "judgment.md": (
            f"---\nname: Judgment Patterns\ndescription: How this user makes decisions\n"
            f"type: judgment\nupdated: {now}\n---\n\n{judgment}"
        ),
        "style.md": (
            f"---\nname: Communication Style\ndescription: How this user communicates and formats output\n"
            f"type: style\nupdated: {now}\n---\n\n{style}"
        ),
        "priorities.md": (
            f"---\nname: Work Priorities\ndescription: What this user focuses on and cares about\n"
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
    """Read existing patterns from output/patterns/. Returns None if not found."""
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
            role_section = (
                f"\n## Role Enhancement: {role.upper()}\n\n"
                f"Incorporate these industry best practices while maintaining "
                f"the user's personal style:\n\n{template}\n"
            )

    custom_section = ""
    if custom_instructions:
        custom_section = f"\n## Additional Instructions\n\n{custom_instructions}\n"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    skill_content = f"""---
name: enhanced-self
description: User's personal behavioral patterns (judgment, style, priorities). Use when writing code, drafting messages, making decisions, or reviewing work for this user.
when_to_use: When drafting emails, writing documents, making decisions, reviewing work, or doing any task on behalf of the user. When the user asks you to act as them or match their style.
---

# Your User's Personal Patterns

Auto-generated by Distill-Me on {now}. When acting on behalf of this user, follow these patterns. Maintain the user's voice — output should feel like it came from them.

## Decision-Making & Judgment

{judgment}

## Communication & Output Style

{style}

## Work Priorities & Focus Areas

{priorities}
{role_section}{custom_section}"""

    return skill_content


def save_skill(skill_content: str) -> str:
    """Save generated skill to skills/enhanced-self/SKILL.md."""
    _ensure_dir(ENHANCED_SKILL_DIR)
    path = ENHANCED_SKILL_DIR / "SKILL.md"
    path.write_text(skill_content, encoding="utf-8")
    return str(path)
