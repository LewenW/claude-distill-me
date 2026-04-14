"""Plus-Me MCP server: scan user data, save patterns, generate skills."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from plus_me.scanner import DataScanner
from plus_me.extractor import PatternExtractor
from plus_me.generator import (
    available_roles,
    generate_skill,
    load_role_template,
    read_patterns,
    save_patterns,
    save_skill,
)

_INSTRUCTIONS = """\
You have access to Plus-Me, a personal skill distillation tool.

Plus-Me scans your Claude data (session logs, memory files, CLAUDE.md) to learn \
how you think, communicate, and make decisions. It then generates a personal \
SKILL.md that makes Claude work like a more professional version of you.

When the user asks to distill their patterns, create their personal skill, or \
wants Claude to "learn" them, use the plus-me tools. The typical flow is:
1. scan_user_data() — collect all available Claude data
2. Analyze the data to extract judgment, style, and priority patterns
3. save_patterns() — persist the extracted patterns
4. generate_personal_skill() — create the final SKILL.md

The generated skill file at skills/enhanced-self/SKILL.md will automatically \
load in future sessions, making Claude behave more like the user.
"""

mcp = FastMCP(
    "plus-me",
    instructions=_INSTRUCTIONS,
)


@mcp.tool()
def scan_user_data() -> str:
    """Scan all local Claude data (session logs, memory files, CLAUDE.md).

    Returns a structured summary of the user's data including conversation
    turns, memory entries, and explicit rules. This data should be analyzed
    to extract behavioral patterns.
    """
    scanner = DataScanner()
    data = scanner.collect_all()
    extractor = PatternExtractor()
    prompts = extractor.prepare_analysis(data)

    result = (
        f"# Plus-Me: User Data Scan Complete\n\n"
        f"## Stats\n"
        f"- Conversation turns: {data.stats['total_turns']}\n"
        f"- Sessions scanned: {data.stats['sessions_scanned']}\n"
        f"- Projects scanned: {data.stats['projects_scanned']}\n"
        f"- Memory entries: {data.stats['total_memories']}\n"
        f"- CLAUDE.md rule files: {data.stats['total_rules']}\n\n"
        f"## Analysis Instructions\n\n"
        f"Now analyze the data below to extract three types of patterns. "
        f"For each, produce a detailed markdown section with specific, "
        f"evidence-backed patterns.\n\n"
        f"### 1. Judgment Patterns (Decision-Making)\n"
        f"{prompts.judgment_prompt}\n\n"
        f"### 2. Communication Style\n"
        f"{prompts.style_prompt}\n\n"
        f"### 3. Work Priorities\n"
        f"{prompts.priorities_prompt}\n"
    )
    return result


@mcp.tool()
def save_extracted_patterns(
    judgment: str,
    style: str,
    priorities: str,
) -> str:
    """Save the extracted user patterns to output/patterns/ directory.

    Args:
        judgment: Markdown describing the user's decision-making patterns.
        style: Markdown describing the user's communication style.
        priorities: Markdown describing the user's work priorities.

    Returns:
        Confirmation with saved file paths.
    """
    saved = save_patterns(judgment, style, priorities)
    paths = "\n".join(f"- {k}: {v}" for k, v in saved.items())
    return f"Patterns saved successfully:\n{paths}"


@mcp.tool()
def generate_personal_skill(
    role: str = "",
    custom_instructions: str = "",
) -> str:
    """Generate the personal SKILL.md from saved patterns + optional role template.

    Must call save_extracted_patterns() first. Reads patterns from disk,
    merges with role best practices, and outputs the final skill.

    Args:
        role: Optional role name for best-practice enhancement (e.g. "pm", "engineering"). Leave empty for pure pattern distillation.
        custom_instructions: Optional additional instructions to include in the skill.

    Returns:
        The generated skill content and save path.
    """
    patterns = read_patterns()
    if not patterns:
        return (
            "Error: No patterns found. Run scan_user_data() and "
            "save_extracted_patterns() first."
        )

    # Strip frontmatter from pattern files for merging
    judgment = _strip_frontmatter(patterns.get("judgment", ""))
    style = _strip_frontmatter(patterns.get("style", ""))
    priorities = _strip_frontmatter(patterns.get("priorities", ""))

    roles = available_roles()
    role_arg = role if role in roles else None
    if role and role not in roles:
        available = ", ".join(roles) if roles else "none"
        return f"Role '{role}' not found. Available roles: {available}"

    skill_content = generate_skill(
        judgment=judgment,
        style=style,
        priorities=priorities,
        role=role_arg,
        custom_instructions=custom_instructions or None,
    )

    path = save_skill(skill_content)
    return (
        f"Personal skill generated and saved to: {path}\n\n"
        f"Available roles for enhancement: {', '.join(roles) if roles else 'none'}\n\n"
        f"---\n\n{skill_content}"
    )


@mcp.tool()
def view_profile() -> str:
    """View the current extracted patterns (user profile).

    Returns the saved judgment, style, and priority patterns,
    or a message if no patterns have been extracted yet.
    """
    patterns = read_patterns()
    if not patterns:
        return (
            "No patterns extracted yet. Run /plus-me:distill to scan "
            "your Claude data and generate your personal profile."
        )

    sections = []
    for name, content in patterns.items():
        sections.append(f"## {name.title()}\n\n{_strip_frontmatter(content)}")

    return "# Your Plus-Me Profile\n\n" + "\n\n---\n\n".join(sections)


def _strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from markdown text."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
