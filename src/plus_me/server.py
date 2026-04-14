"""Plus-Me MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from plus_me.scanner import DataScanner
from plus_me.extractor import prepare_for_analysis
from plus_me.generator import (
    available_roles,
    generate_skill,
    read_patterns,
    save_patterns,
    save_skill,
)

_INSTRUCTIONS = """\
You have Plus-Me, a personal skill distillation tool.

It scans your Claude data (session logs, memory files, CLAUDE.md, \
memory-bridge namespaces, claude.ai exports) to learn how you think \
and communicate. It generates a personal SKILL.md that makes Claude \
work more like you.

Flow: scan_user_data() → analyze the output → save_extracted_patterns() \
→ generate_personal_skill().
"""

mcp = FastMCP("plus-me", instructions=_INSTRUCTIONS)


@mcp.tool()
def scan_user_data() -> str:
    """Scan local Claude data and return structured content for pattern analysis.

    Reads session logs, memory files, CLAUDE.md rules, memory-bridge
    namespaces, and claude.ai exports. Returns data + analysis prompts.
    Claude does the actual pattern extraction from this output.
    """
    scanner = DataScanner()
    data = scanner.collect_all()
    bundle = prepare_for_analysis(data)

    stats = data.stats
    return (
        f"# Scan Complete\n\n"
        f"**{stats['total_turns']}** turns "
        f"({stats['session_turns']} from sessions, "
        f"{stats['exported_turns']} from exports) | "
        f"**{stats['sessions_scanned']}** sessions | "
        f"**{stats['projects_scanned']}** projects | "
        f"**{stats['total_memories']}** memories "
        f"({stats['project_memories']} project, "
        f"{stats['bridge_memories']} bridge) | "
        f"**{stats['total_rules']}** rule files\n\n"
        f"---\n\n"
        f"Analyze the data below. Extract three pattern categories.\n\n"
        f"## 1. Judgment Patterns\n\n{bundle.judgment_prompt}\n\n"
        f"## 2. Communication Style\n\n{bundle.style_prompt}\n\n"
        f"## 3. Work Priorities\n\n{bundle.priorities_prompt}\n"
    )


@mcp.tool()
def save_extracted_patterns(
    judgment: str,
    style: str,
    priorities: str,
) -> str:
    """Save extracted patterns to disk.

    Args:
        judgment: User's decision-making patterns (markdown).
        style: User's communication style (markdown).
        priorities: User's work priorities (markdown).
    """
    saved = save_patterns(judgment, style, priorities)
    paths = "\n".join(f"- {k}: {v}" for k, v in saved.items())
    return f"Saved:\n{paths}"


@mcp.tool()
def generate_personal_skill(
    role: str = "",
    custom_instructions: str = "",
) -> str:
    """Generate SKILL.md from saved patterns + optional role template.

    Call save_extracted_patterns() first.

    Args:
        role: Role name for best-practice fusion (e.g. "pm"). Empty for pure distillation.
        custom_instructions: Extra instructions to include.
    """
    patterns = read_patterns()
    if not patterns:
        return "No patterns found. Run scan_user_data() and save_extracted_patterns() first."

    judgment = _strip_frontmatter(patterns.get("judgment", ""))
    style = _strip_frontmatter(patterns.get("style", ""))
    priorities = _strip_frontmatter(patterns.get("priorities", ""))

    roles = available_roles()
    if role and role not in roles:
        return f"Role '{role}' not found. Available: {', '.join(roles) if roles else 'none'}"

    role_arg = role if role in roles else None
    skill_content = generate_skill(
        judgment=judgment,
        style=style,
        priorities=priorities,
        role=role_arg,
        custom_instructions=custom_instructions or None,
    )

    path = save_skill(skill_content)
    return f"Saved to: {path}\n\nAvailable roles: {', '.join(roles) if roles else 'none'}\n\n---\n\n{skill_content}"


@mcp.tool()
def view_profile() -> str:
    """View current extracted patterns."""
    patterns = read_patterns()
    if not patterns:
        return "No patterns yet. Run /plus-me:distill first."

    sections = []
    for name, content in patterns.items():
        sections.append(f"## {name.title()}\n\n{_strip_frontmatter(content)}")

    return "# Your Profile\n\n" + "\n\n---\n\n".join(sections)


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
