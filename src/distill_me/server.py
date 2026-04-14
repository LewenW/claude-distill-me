"""Distill-Me MCP server — 3 tools for deep behavioral distillation."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from distill_me.scanner import DataScanner
from distill_me.extractor import prepare_for_analysis
from distill_me.generator import (
    _strip_frontmatter,
    available_roles,
    generate_skill,
    inject_into_claude_md,
    read_patterns,
    save_patterns,
    save_skill,
)

_INSTRUCTIONS = """\
You have Distill-Me, a deep behavioral distillation tool.

Distill-Me scans your Claude session history, memory files, and CLAUDE.md \
rules across all projects. It extracts behavioral patterns at three depths:

1. **Observable** — what you explicitly say and do
2. **Interpretive** — what your patterns reveal about how you think
3. **Contrastive** — what makes you DIFFERENT from most people

Run /distill-me:distill to generate your personal skill. The output goes \
to both the plugin's SKILL.md and your ~/.claude/CLAUDE.md (loads everywhere).

Flow: scan_user_data() → analyze → save_extracted_patterns() → \
generate_personal_skill().
"""

mcp = FastMCP("distill-me", instructions=_INSTRUCTIONS)


def _safe(fn):
    import functools

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return f"Error in {fn.__name__}: {type(e).__name__}: {e}"

    return wrapper


@mcp.tool()
@_safe
def scan_user_data() -> str:
    """Scan local Claude data for deep behavioral analysis.

    Collects session logs, memory files, CLAUDE.md rules, and
    memory-bridge namespaces. Returns data + three-layer extraction
    prompts for Claude to analyze.
    """
    scanner = DataScanner()
    data = scanner.collect_all()
    bundle = prepare_for_analysis(data)
    stats = data.stats

    low_data_warning = ""
    if stats["total_turns"] < 20 or stats["sessions_scanned"] < 3:
        low_data_warning = (
            "**Low data.** Pattern depth improves with more sessions. "
            "Consider running distill again after a few more days of use.\n\n"
        )

    return (
        f"# Scan Complete\n\n"
        f"**{stats['total_turns']}** turns | "
        f"**{stats['sessions_scanned']}** sessions | "
        f"**{stats['projects_scanned']}** projects | "
        f"**{stats['total_memories']}** memories "
        f"({stats['project_memories']} project, "
        f"{stats['bridge_memories']} bridge) | "
        f"**{stats['total_rules']}** rule files\n\n"
        f"{low_data_warning}"
        f"---\n\n"
        f"Analyze ALL the Collected Data below using three-layer extraction "
        f"(Observable → Interpretive → Contrastive). Be specific and "
        f"evidence-backed. Go deep — extract HOW this user thinks, not just "
        f"WHAT they prefer.\n\n"
        f"For each pattern:\n"
        f"- **Pattern**: When [situation], this user [behavior] because [reason]\n"
        f"- **Evidence**: [specific example from data]\n"
        f"- **Confidence**: high/medium/low\n"
        f"- **Depth**: surface / interpretive / deep\n\n"
        f"{bundle.data_summary}\n\n"
        f"---\n\n"
        f"## 1. Decision-Making & Cognitive Patterns\n\n{bundle.judgment_prompt}\n\n"
        f"## 2. Communication & Personality\n\n{bundle.style_prompt}\n\n"
        f"## 3. Values & Work Philosophy\n\n{bundle.priorities_prompt}\n"
    )


@mcp.tool()
@_safe
def save_extracted_patterns(
    judgment: str,
    style: str,
    priorities: str,
) -> str:
    """Save extracted patterns to disk.

    Args:
        judgment: Decision-making and cognitive patterns (markdown).
        style: Communication and personality patterns (markdown).
        priorities: Values and work philosophy (markdown).
    """
    saved = save_patterns(judgment, style, priorities)
    paths = "\n".join(f"- {k}: {v}" for k, v in saved.items())
    return f"Saved:\n{paths}"


@mcp.tool()
@_safe
def generate_personal_skill(
    role: str = "",
    custom_instructions: str = "",
) -> str:
    """Generate SKILL.md from saved patterns + optional role fusion.

    Call save_extracted_patterns() first.

    Args:
        role: Role template to fuse with (e.g. "pm"). Empty for pure distillation.
        custom_instructions: Extra instructions to include.
    """
    patterns = read_patterns()
    if not patterns:
        return "No patterns found. Run scan_user_data() and save_extracted_patterns() first."

    judgment = _strip_frontmatter(patterns.get("judgment", ""))
    style = _strip_frontmatter(patterns.get("style", ""))
    priorities = _strip_frontmatter(patterns.get("priorities", ""))

    roles = available_roles()
    role_arg = None
    if role:
        if role in roles:
            role_arg = role
        else:
            matches = [r for r in roles if role.lower() in r.lower()]
            if len(matches) == 1:
                role_arg = matches[0]
            elif len(matches) > 1:
                return (
                    f"Multiple roles match '{role}':\n"
                    + "\n".join(f"- {r}" for r in matches)
                    + "\n\nSpecify the full name."
                )
            else:
                return (
                    f"No role matching '{role}'. Available:\n"
                    + "\n".join(f"- {r}" for r in roles)
                )

    skill_content = generate_skill(
        judgment=judgment,
        style=style,
        priorities=priorities,
        role=role_arg,
        custom_instructions=custom_instructions or None,
    )

    skill_path = save_skill(skill_content)
    claude_md_path = inject_into_claude_md(skill_content)

    return (
        f"Saved to:\n"
        f"- Plugin skill: {skill_path}\n"
        f"- Global config: {claude_md_path}\n\n"
        f"Available roles for fusion: {', '.join(roles) if roles else 'none'}\n\n"
        f"---\n\n{skill_content}"
    )


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
