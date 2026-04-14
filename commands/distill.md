---
name: distill
description: Deep behavioral distillation — extract how you think, decide, and communicate
argument-hint: "[role]"
---

# Distill

Extract deep behavioral patterns from your Claude data and generate a personal skill.

## Steps

1. Call `scan_user_data()`. This collects:
   - Session logs (last 30 days, all projects)
   - Memory files (project + memory-bridge)
   - CLAUDE.md rules (global + per-project)

2. Analyze ALL data using three-layer extraction:

   **Layer 1 — Observable:** What you can directly see in the data.
   **Layer 2 — Interpretive:** What the patterns reveal about deeper traits.
   **Layer 3 — Contrastive:** What makes this user DIFFERENT from most people.

   Extract patterns in three categories:

   **Decision-Making & Cognitive Patterns:**
   - How they choose, what frameworks they use implicitly
   - Risk tolerance, ambiguity response, trust architecture
   - Guardrails and what they reveal about past experiences
   - What's unique about their reasoning

   **Communication & Personality:**
   - Voice, language mixing, message length, formatting
   - Relationship with AI, emotional register, feedback patterns
   - What makes their voice unmistakable
   - Gap between how they write and how they want YOU to write

   **Values & Work Philosophy:**
   - What they optimize for (stated vs revealed)
   - Values hierarchy — when two priorities conflict, which wins?
   - Connecting theme across disparate decisions
   - Meta-cognition: how they learn, respond to mistakes

   Each pattern must have:
   - **Pattern**: When [situation], this user [behavior] because [reason]
   - **Evidence**: specific quote or behavior
   - **Confidence**: high / medium / low
   - **Depth**: surface / interpretive / deep

   Aim for 10-20 patterns per category. Go deep. "Prefers Python" is surface — "reaches for Python because they value readability over performance, and will only switch languages when forced by ecosystem constraints" is deep.

3. Call `save_extracted_patterns()` with three markdown strings.

4. Call `generate_personal_skill()`. Pass the `role` argument if specified.

5. Show 5-8 of the deepest, most distinctive patterns found. Ask if anything is wrong or missing — user corrections are the highest-quality signal.

Output locations:
- `skills/enhanced-self/SKILL.md` (plugin skill)
- `~/.claude/CLAUDE.md` (loads everywhere — CLI, Desktop, Cowork)

Re-run anytime to update with new data.
