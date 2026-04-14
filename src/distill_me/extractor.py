"""Deep behavioral extraction prompts.

Three-layer analysis: Observable → Interpretive → Contrastive.
Each layer builds on the previous, extracting increasingly deep patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from distill_me.config import MAX_ANALYSIS_TURNS, MAX_MEMORY_CHARS
from distill_me.scanner import UserData


@dataclass
class AnalysisBundle:
    """Data + deep extraction prompts for Claude to analyze."""
    data_summary: str
    judgment_prompt: str
    style_prompt: str
    priorities_prompt: str


def _format_turns(data: UserData, max_turns: int = MAX_ANALYSIS_TURNS) -> str:
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
        content = mem.content[:MAX_MEMORY_CHARS]
        if len(mem.content) > MAX_MEMORY_CHARS:
            content += " [...]"
        lines.append(content)
        lines.append("")
    return "\n".join(lines)


def _format_rules(data: UserData) -> str:
    if not data.claude_md_rules:
        return "(none)"
    return "\n\n".join(data.claude_md_rules)


def prepare_for_analysis(data: UserData) -> AnalysisBundle:
    """Build data summary and deep extraction prompts."""
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

    # --- DEEP EXTRACTION PROMPTS ---
    # Three-layer analysis per category:
    #   Layer 1 (Observable): what you can directly see in the data
    #   Layer 2 (Interpretive): what the patterns imply about deeper traits
    #   Layer 3 (Contrastive): what makes this user DIFFERENT from most people

    judgment_prompt = """\
Extract this user's **decision-making patterns and cognitive DNA**.

### Layer 1: Observable Decisions
Catalog concrete decisions from the data:
- What do they accept without pushback vs correct or reject?
- What scope choices do they make? What gets cut, what's sacred?
- What guardrails have they set on AI behavior?
- When presented with options, which do they pick and how fast?

### Layer 2: Underlying Frameworks
Interpret WHAT the decisions reveal about HOW they think:
- What implicit decision framework are they using? (evidence-driven? \
intuition? speed-first? correctness-first?)
- Risk calibration: do they ship and iterate, or polish before release? \
Where on this spectrum and does it shift by context?
- Ambiguity response: when something is unclear, do they ask, assume, \
research, or demand your honest opinion?
- Trust architecture: what do they verify themselves vs delegate? What \
triggers distrust?
- Quality threshold: what makes them say "this isn't good enough" vs \
"good enough, ship it"?

### Layer 3: Contrastive Analysis
Find what's UNIQUE about this person's reasoning:
- What does this user do DIFFERENTLY from most Claude users when making \
decisions?
- What do their guardrails reveal about past bad experiences?
- What contradictions exist in their decision patterns, and what do those \
contradictions reveal about their actual priorities?
- If you had to predict their reaction to a new situation, what mental \
model would you use?

Format each pattern as:
- **Pattern**: When [situation], this user [specific behavior] because \
[underlying reason].
- **Evidence**: [direct quote or specific example]
- **Confidence**: high/medium/low
- **Depth**: surface / interpretive / deep

Extract 10-20 patterns across all three layers. Go beyond "they prefer X" \
— explain WHY they prefer X and what it reveals about how they think."""

    style_prompt = """\
Extract this user's **communication patterns and personality signature**.

### Layer 1: Observable Voice
Map the surface-level communication patterns:
- Message length distribution — 2-word commands or paragraph briefs?
- Language patterns — which language for what? Which terms stay in English?
- Formatting habits — tables, bullets, code blocks, prose? When each?
- Correction style — direct ("no, X") or indirect ("actually, maybe Y")?
- Request style — terse commands or detailed specifications?

### Layer 2: Personality Through Communication
Read between the lines for personality traits:
- Relationship with AI — peer? tool? subordinate? Does this shift by task?
- Emotional register — when do they get excited, frustrated, dismissive, \
playful? What triggers each?
- Feedback patterns — do they praise? How? What does silence mean?
- Information density preference — do they want summaries or raw data? \
Context or just answers?
- What they HATE in output — not just banned words, but what kind of \
thinking produces output they reject?

### Layer 3: Contrastive Voice Analysis
Find what makes this person's voice unmistakable:
- What would be the WORST way to communicate with this user? (This \
defines their style by negation)
- If you had to write a message AS this person, what would feel wrong to \
include? What would be missing if left out?
- What's the gap between how they write and how they want YOU to write? \
(They may be terse but expect thorough output, or verbose but want \
brevity from you)
- How does their communication style differ from their stated preferences?

Format each pattern with evidence and confidence. Include direct quotes \
where possible. Patterns should be specific enough that someone reading \
them could successfully imitate this user's voice."""

    priorities_prompt = """\
Extract this user's **values hierarchy and work philosophy**.

### Layer 1: Observable Focus
Map what they actually spend time on:
- Task types initiated most frequently
- What they delegate to AI vs do themselves
- What gets reviewed carefully vs rubber-stamped
- Tools, frameworks, platforms they keep returning to
- Ship cadence — daily deploys or careful releases?

### Layer 2: Underlying Values
Interpret what the focus patterns reveal:
- What do they optimize for that they never explicitly state?
- What recurring frustrations hint at deeper concerns?
- What's their implicit theory of quality? Of productivity? Of success?
- When two priorities conflict, which consistently wins?
- What do they spend energy on that most people in their role wouldn't?
- What do they skip that most people in their role wouldn't skip?

### Layer 3: Contrastive Values
Find what's uniquely important to this person:
- What do they care about that most users don't?
- If forced to sacrifice one value for another, which survives? Build a \
rough hierarchy.
- What's the connecting theme across their disparate decisions? (There's \
usually one or two root values driving everything)
- What would they never compromise on even under pressure?
- How do their stated priorities differ from their revealed priorities \
(based on where they actually spend attention)?

### Meta-Cognition (if enough data)
- How do they learn new things? Jump in and iterate, or study first?
- How do they respond to their own mistakes vs others' mistakes?
- What triggers them to step back and rethink vs push forward?

Format each pattern with evidence and confidence. Group by theme. Every \
pattern should answer "so what?" — why does this matter for how I should \
work with this person?"""

    return AnalysisBundle(
        data_summary=data_summary,
        judgment_prompt=judgment_prompt,
        style_prompt=style_prompt,
        priorities_prompt=priorities_prompt,
    )
