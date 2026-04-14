"""Prepare user data and analysis prompts for Claude to extract patterns."""

from __future__ import annotations

from dataclasses import dataclass
from plus_me.scanner import UserData


@dataclass
class AnalysisBundle:
    """Data + prompts ready for Claude to analyze. Not the patterns themselves."""
    data_summary: str
    judgment_prompt: str
    style_prompt: str
    priorities_prompt: str


def _format_turns(data: UserData, max_turns: int = 80) -> str:
    lines: list[str] = []
    for i, turn in enumerate(data.turns[:max_turns]):
        lines.append(f"--- Turn {i+1} [project: {turn.project}] ---")
        lines.append(f"USER: {turn.user_message}")
        lines.append(f"ASSISTANT: {turn.assistant_message}")
        lines.append("")
    return "\n".join(lines)


def _format_memories(data: UserData) -> str:
    if not data.memories:
        return "(none)"
    lines: list[str] = []
    for mem in data.memories:
        lines.append(f"--- [{mem.memory_type}] {mem.name} ---")
        if mem.description:
            lines.append(f"Description: {mem.description}")
        if mem.tags:
            lines.append(f"Tags: {', '.join(mem.tags)}")
        lines.append(mem.content[:500])
        lines.append("")
    return "\n".join(lines)


def _format_rules(data: UserData) -> str:
    if not data.claude_md_rules:
        return "(none)"
    return "\n\n".join(data.claude_md_rules)


def prepare_for_analysis(data: UserData) -> AnalysisBundle:
    """Build the data summary and analysis prompts. Claude does the actual extraction."""
    turns_text = _format_turns(data)
    memories_text = _format_memories(data)
    rules_text = _format_rules(data)

    data_summary = (
        f"## Collected Data\n\n"
        f"**Stats:** {data.stats['total_turns']} turns from "
        f"{data.stats['sessions_scanned']} sessions across "
        f"{data.stats['projects_scanned']} projects. "
        f"{data.stats['total_memories']} memory entries. "
        f"{data.stats['total_rules']} rule files.\n\n"
        f"### Conversations\n\n{turns_text}\n\n"
        f"### Memories\n\n{memories_text}\n\n"
        f"### CLAUDE.md Rules\n\n{rules_text}"
    )

    judgment_prompt = (
        "From the data below, extract this user's **decision-making patterns**.\n\n"
        "Look for:\n"
        "- How they evaluate options and make choices\n"
        "- When they accept vs reject suggestions (and why)\n"
        "- Risk tolerance and quality standards\n"
        "- Trade-off approaches and prioritization heuristics\n\n"
        "Format: '- When [situation], this user tends to [pattern]. "
        "Evidence: [specific example from data]'\n\n"
        "Be specific. No generic statements.\n\n"
        f"{data_summary}"
    )

    style_prompt = (
        "From the data below, extract this user's **communication style**.\n\n"
        "Look for:\n"
        "- Message length and detail level\n"
        "- Language (Chinese/English/mixed) and tone\n"
        "- Request structure and feedback phrasing\n"
        "- Formatting preferences\n"
        "- How they phrase corrections\n\n"
        "Include concrete examples from the data.\n\n"
        f"{data_summary}"
    )

    priorities_prompt = (
        "From the data below, extract this user's **work priorities**.\n\n"
        "Look for:\n"
        "- Task types they prioritize\n"
        "- What they delegate vs do themselves\n"
        "- Recurring topics and concerns\n"
        "- What they skip or deprioritize\n"
        "- Tools and frameworks they favor\n\n"
        "Group by theme. Include evidence.\n\n"
        f"{data_summary}"
    )

    return AnalysisBundle(
        data_summary=data_summary,
        judgment_prompt=judgment_prompt,
        style_prompt=style_prompt,
        priorities_prompt=priorities_prompt,
    )
