"""Prepare user data for pattern extraction by Claude."""

from __future__ import annotations

from dataclasses import dataclass
from plus_me.scanner import UserData


@dataclass
class AnalysisPrompts:
    """Structured prompts for Claude to analyze user patterns."""
    judgment_prompt: str
    style_prompt: str
    priorities_prompt: str
    data_summary: str


@dataclass
class Patterns:
    """Extracted user patterns (markdown strings)."""
    judgment: str
    style: str
    priorities: str


def _format_turns_for_analysis(data: UserData, max_turns: int = 80) -> str:
    """Format conversation turns into a readable analysis block."""
    lines: list[str] = []
    for i, turn in enumerate(data.turns[:max_turns]):
        lines.append(f"--- Turn {i+1} [project: {turn.project}] ---")
        lines.append(f"USER: {turn.user_message}")
        lines.append(f"ASSISTANT: {turn.assistant_message}")
        lines.append("")
    return "\n".join(lines)


def _format_memories_for_analysis(data: UserData) -> str:
    """Format memory entries into a readable block."""
    if not data.memories:
        return "(No memory files found)"
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


def _format_rules_for_analysis(data: UserData) -> str:
    """Format CLAUDE.md rules into a readable block."""
    if not data.claude_md_rules:
        return "(No CLAUDE.md files found)"
    return "\n\n".join(data.claude_md_rules)


class PatternExtractor:
    """Prepares structured data and prompts for Claude to extract patterns."""

    def prepare_analysis(self, data: UserData) -> AnalysisPrompts:
        """Build analysis prompts from collected user data."""
        turns_text = _format_turns_for_analysis(data)
        memories_text = _format_memories_for_analysis(data)
        rules_text = _format_rules_for_analysis(data)

        data_summary = (
            f"## Collected User Data\n\n"
            f"**Stats:** {data.stats['total_turns']} conversation turns from "
            f"{data.stats['sessions_scanned']} sessions across "
            f"{data.stats['projects_scanned']} projects. "
            f"{data.stats['total_memories']} memory entries. "
            f"{data.stats['total_rules']} CLAUDE.md rule files.\n\n"
            f"### Conversation History\n\n{turns_text}\n\n"
            f"### Memory Files\n\n{memories_text}\n\n"
            f"### CLAUDE.md Rules\n\n{rules_text}"
        )

        judgment_prompt = (
            "Analyze the following user data from their Claude interactions. "
            "Extract their **decision-making patterns**:\n\n"
            "Focus on:\n"
            "- How they evaluate options and make choices\n"
            "- When they accept vs reject Claude's suggestions (and why)\n"
            "- Their risk tolerance and quality standards\n"
            "- Their approach to trade-offs and prioritization\n"
            "- Recurring decision frameworks or heuristics they use\n\n"
            "Output a structured markdown document with specific, "
            "actionable patterns (not vague generalizations). "
            "Use format: '- When [situation], this user tends to [pattern]. "
            "Evidence: [specific example from data]'\n\n"
            f"{data_summary}"
        )

        style_prompt = (
            "Analyze the following user data from their Claude interactions. "
            "Extract their **communication and output style**:\n\n"
            "Focus on:\n"
            "- Message length and detail level preferences\n"
            "- Language (Chinese/English/mixed) and tone\n"
            "- How they structure requests and feedback\n"
            "- Formatting preferences (markdown, lists, code blocks)\n"
            "- Whether they prefer concise or detailed responses\n"
            "- How they phrase corrections and follow-ups\n\n"
            "Output a structured markdown document with specific patterns. "
            "Include concrete examples from the data.\n\n"
            f"{data_summary}"
        )

        priorities_prompt = (
            "Analyze the following user data from their Claude interactions. "
            "Extract their **work priorities and focus areas**:\n\n"
            "Focus on:\n"
            "- What types of tasks they prioritize\n"
            "- What they tend to delegate vs do themselves\n"
            "- Topics they repeatedly return to or care deeply about\n"
            "- What they skip, ignore, or deprioritize\n"
            "- Their working rhythm (deep work vs quick tasks)\n"
            "- Tools, frameworks, and technologies they favor\n\n"
            "Output a structured markdown document with specific patterns. "
            "Group by theme. Include evidence from the data.\n\n"
            f"{data_summary}"
        )

        return AnalysisPrompts(
            judgment_prompt=judgment_prompt,
            style_prompt=style_prompt,
            priorities_prompt=priorities_prompt,
            data_summary=data_summary,
        )
