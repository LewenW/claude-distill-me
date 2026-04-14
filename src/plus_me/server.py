"""Plus-Me MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from plus_me.scanner import DataScanner
from plus_me.extractor import prepare_for_analysis
from plus_me.queue import effective_confidence, load_queue, prune_stale, queue_stats
from plus_me.generator import (
    available_roles,
    generate_skill,
    read_patterns,
    save_patterns,
    save_skill,
)

_INSTRUCTIONS = """\
You have Plus-Me, a continuous learning tool for personal skill distillation.

Plus-Me learns from you in two ways:
1. **Real-time**: Hooks capture corrections, preferences, and feedback from \
every message you send (stored in a learning queue)
2. **On-demand**: /plus-me:distill scans session history + queued learnings \
to extract deep behavioral patterns

The learning queue accumulates signals over time. Each /distill run \
synthesizes all available data (queue + sessions + memories) into a \
personal SKILL.md that makes Claude work more like you.

Flow: scan_user_data() → analyze → save_extracted_patterns() → \
generate_personal_skill().
"""

mcp = FastMCP("plus-me", instructions=_INSTRUCTIONS)


@mcp.tool()
def scan_user_data() -> str:
    """Scan local Claude data + learning queue for pattern analysis.

    Collects session logs, memory files, CLAUDE.md rules, memory-bridge
    namespaces, claude.ai exports, AND queued real-time learnings.
    Returns data + analysis prompts for Claude to extract patterns.
    """
    scanner = DataScanner()
    data = scanner.collect_all()
    bundle = prepare_for_analysis(data)

    # Prune stale items, then collect queued learnings
    for proj_dir in _scan_project_dirs():
        prune_stale(proj_dir)
    prune_stale()

    all_queued: list[dict] = []
    for proj_dir in _scan_project_dirs():
        all_queued.extend(load_queue(proj_dir))
    all_queued.extend(load_queue())

    queue_section = ""
    if all_queued:
        queue_section = _format_queue(all_queued)

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
        f"**{stats['total_rules']}** rule files | "
        f"**{len(all_queued)}** queued learnings\n\n"
        f"---\n\n"
        f"{queue_section}"
        f"Analyze ALL data below (including queued learnings — these are "
        f"high-signal corrections and preferences captured in real-time). "
        f"Extract three pattern categories. Be specific and evidence-backed.\n\n"
        f"For each pattern, use this format:\n"
        f"- **Pattern**: [concise statement]\n"
        f"- **Evidence**: [specific example from the data]\n"
        f"- **Confidence**: high/medium/low\n\n"
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
    """View current extracted patterns and learning queue stats."""
    patterns = read_patterns()

    # Gather queue stats across projects
    total_queued = 0
    total_stale = 0
    for proj_dir in _scan_project_dirs():
        s = queue_stats(proj_dir)
        total_queued += s["total"]
        total_stale += s.get("stale", 0)
    global_stats = queue_stats()
    total_queued += global_stats["total"]
    total_stale += global_stats.get("stale", 0)

    if not patterns and total_queued == 0:
        return "No patterns or learnings yet. Run /plus-me:distill first."

    parts = []
    if patterns:
        for name, content in patterns.items():
            parts.append(f"## {name.title()}\n\n{_strip_frontmatter(content)}")

    active = total_queued - total_stale
    queue_msg = f"\n\n---\n\n**Learning queue:** {active} active items"
    if total_stale:
        queue_msg += f" ({total_stale} stale)"
    queue_msg += "."
    if active >= 10:
        queue_msg += " Run /plus-me:distill to incorporate them."

    profile = "# Your Profile\n\n" + "\n\n---\n\n".join(parts) if parts else "# No patterns extracted yet"
    return profile + queue_msg


@mcp.tool()
def view_queue() -> str:
    """View the real-time learning queue (captured corrections, preferences, feedback)."""
    all_items: list[dict] = []
    for proj_dir in _scan_project_dirs():
        all_items.extend(load_queue(proj_dir))
    all_items.extend(load_queue())

    if not all_items:
        return "Learning queue is empty. As you use Claude, corrections and preferences are captured automatically."

    all_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    lines = [f"# Learning Queue ({len(all_items)} items)\n"]
    for item in all_items[:50]:
        msg = item.get("message", "")[:80]
        ltype = item.get("learning_type", "?")
        eff = effective_confidence(item)
        ts = item.get("timestamp", "")[:10]
        lines.append(f"- [{ltype}] ({eff:.0%}) {msg} — {ts}")

    if len(all_items) > 50:
        lines.append(f"\n... and {len(all_items) - 50} more")

    return "\n".join(lines)


def _format_queue(items: list[dict]) -> str:
    """Format queued learnings for inclusion in analysis."""
    lines = ["## Queued Real-Time Learnings\n",
             "These are high-signal corrections and preferences captured "
             "from individual messages. Weight them heavily.\n"]
    for item in items:
        ltype = item.get("learning_type", "?")
        eff = effective_confidence(item)
        msg = item.get("message", "")
        lines.append(f"- **[{ltype}, {eff:.0%}]** {msg}")
    lines.append("\n---\n")
    return "\n".join(lines)


def _scan_project_dirs() -> list[str]:
    """Get list of project directories that might have queues."""
    from plus_me.config import PROJECTS_DIR
    if not PROJECTS_DIR.exists():
        return []
    return [str(d) for d in PROJECTS_DIR.iterdir() if d.is_dir()]


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
