"""Prepare user data and analysis prompts for Claude to extract patterns."""

from __future__ import annotations

from dataclasses import dataclass
from distill_me.scanner import UserData


@dataclass
class AnalysisBundle:
    """Data + prompts ready for Claude to analyze. Not the patterns themselves."""
    data_summary: str
    judgment_prompt: str
    style_prompt: str
    priorities_prompt: str


def _format_turns(data: UserData, max_turns: int = 80, queued_messages: set[str] | None = None) -> str:
    lines: list[str] = []
    for i, turn in enumerate(data.turns[:max_turns]):
        # Skip turns already captured in the learning queue
        if queued_messages and turn.user_message[:80] in queued_messages:
            continue
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
        content = mem.content[:500]
        if len(mem.content) > 500:
            content += " [...]"
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def _format_rules(data: UserData) -> str:
    if not data.claude_md_rules:
        return "(none)"
    return "\n\n".join(data.claude_md_rules)


def prepare_for_analysis(data: UserData, queued_messages: list[str] | None = None) -> AnalysisBundle:
    """Build the data summary and analysis prompts. Claude does the actual extraction.

    queued_messages: message strings already in the learning queue.
    Turns matching these are excluded to avoid double-weighting.
    """
    queued_set = {m[:80] for m in queued_messages} if queued_messages else None
    turns_text = _format_turns(data, queued_messages=queued_set)
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

    # Prompts reference the data by section header — the data is included
    # once in the server's scan_user_data() output, not repeated per prompt.
    judgment_prompt = (
        "Extract this user's **decision-making and judgment patterns** "
        "from the Collected Data above.\n\n"
        "Go beyond surface preferences. Look for HOW they think:\n"
        "- When presented with options, how do they choose? (data-driven? gut? "
        "speed-first? quality-first?)\n"
        "- What do they accept without pushback vs what triggers corrections?\n"
        "- How do they handle ambiguity — do they ask, assume, or demand your "
        "honest opinion?\n"
        "- Risk tolerance: do they ship fast and iterate, or polish before release?\n"
        "- Scope decisions: what gets cut and what's non-negotiable?\n"
        "- Guardrails: what have they explicitly told Claude NOT to do?\n"
        "- Quality bar: what triggers 'this isn't good enough'?\n"
        "- When do they trust external input (e.g. claude.ai reviews) vs verify "
        "themselves?\n\n"
        "Format each pattern as:\n"
        "- **Pattern**: When [situation], this user [specific behavior].\n"
        "- **Evidence**: [direct quote or specific example from the data]\n"
        "- **Confidence**: high/medium/low\n\n"
        "Aim for 8-15 patterns. Every pattern must be specific enough that "
        "another person reading it would change their behavior."
    )

    style_prompt = (
        "Extract this user's **communication and output style** "
        "from the Collected Data above.\n\n"
        "Look for patterns that would let you replicate their voice:\n"
        "- Message length distribution — are they a 2-word person or "
        "paragraph-writer?\n"
        "- Language mixing — which language for what context? Which technical "
        "terms stay in English?\n"
        "- Tone — formal, casual, playful, blunt, self-deprecating?\n"
        "- How they phrase corrections — direct ('no, X') vs indirect "
        "('actually, maybe Y')?\n"
        "- What they hate in output — banned words, AI-sounding phrases, "
        "excessive explanation?\n"
        "- Formatting preferences — tables vs bullets vs prose? When?\n"
        "- How they request work — short commands ('推') vs detailed briefs?\n"
        "- Response expectations — do they want summaries or just action?\n\n"
        "Include direct quotes. Patterns should be specific enough to "
        "reproduce the user's voice in writing."
    )

    priorities_prompt = (
        "Extract this user's **work priorities and focus areas** "
        "from the Collected Data above.\n\n"
        "Look for what drives their decisions day-to-day:\n"
        "- What task types do they initiate most? What do they never start?\n"
        "- What do they delegate to Claude vs do themselves?\n"
        "- What gets reviewed carefully vs rubber-stamped?\n"
        "- What recurring themes or concerns appear across sessions?\n"
        "- What tools, frameworks, or platforms do they keep coming back to?\n"
        "- Ship cadence — fast daily deploys or careful weekly releases?\n"
        "- What external metrics matter to them (stars, downloads, user "
        "feedback)?\n"
        "- What do they deprioritize or explicitly skip?\n\n"
        "Group by theme. Each pattern needs evidence."
    )

    return AnalysisBundle(
        data_summary=data_summary,
        judgment_prompt=judgment_prompt,
        style_prompt=style_prompt,
        priorities_prompt=priorities_prompt,
    )
