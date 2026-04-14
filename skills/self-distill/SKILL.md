---
name: self-distill
description: Guides Plus-Me continuous learning and distillation. Activates when user wants to create/update their personal skill or when Plus-Me tools are used.
version: 0.2.0
---

# Plus-Me Continuous Learning Guide

## Two Learning Layers

### Real-Time (Automatic)
UserPromptSubmit hook captures corrections, preferences, and feedback from every message. These are queued as structured learning items with confidence scores.

### On-Demand (/distill)
Full synthesis: queue + session history + memories → patterns → SKILL.md.

## When to Suggest Distillation

- Queue has 10+ items (check with view_queue)
- User asks to "learn me" or "understand my style"
- User wants a personal skill or personalized agent
- Last distill was over a week ago

## Extraction Quality Standards

Each pattern MUST have:
- **Pattern**: concise, actionable ("Prefers 3-bullet summaries" not "likes brevity")
- **Evidence**: specific quote or behavior from the data
- **Confidence**: high / medium / low

Aim for 8-15 patterns per category. More is better than fewer, as long as each is evidence-backed.

### Judgment — look for:
- Accept/reject patterns on suggestions
- How they handle ambiguity (ask vs assume)
- Risk tolerance (conservative vs aggressive)
- Quality vs speed trade-offs
- How they triage bug reports or reviews
- Guardrails set on AI behavior ("don't X unless", "only do what I asked")

### Style — look for:
- Language code-switching patterns (Chinese/English/mixed)
- Message length distribution (short commands vs detailed briefs)
- Formatting preferences (tables, bullets, code blocks, prose)
- Correction phrasing patterns
- Tone (formal, casual, playful, direct)

### Priorities — look for:
- Task types initiated most often
- What gets corrected or pushed back on
- What gets skipped or accepted without review
- Recurring themes and tools across sessions
- Ship cadence and quality bar

## Queued Learnings are High Signal

Items in the learning queue were captured in real-time from actual corrections and preferences. They represent the user's most explicit signals. Weight them more heavily than inferred patterns from session history.

Before extracting, validate each queued item:
- Filter out one-time instructions (not generalizable)
- Resolve contradictions (keep the more recent signal)
- Note the effective confidence (decays over time)

## Contradiction Detection

When extracting patterns, check for internal contradictions:
- Two patterns giving opposite advice on the same topic
- New queue items that override older patterns
- Keep the most recent, evidence-backed version

## After Distillation

Let the user review. User corrections to the generated patterns are themselves high-quality learnings — incorporate them immediately.
