---
name: distill
description: Synthesize all data (sessions + queue + memories) into your personal skill
argument-hint: "[role]"
---

# Distill

Synthesize queued learnings + session history + memories into a personal skill.

## Steps

1. Call `scan_user_data()`. This collects:
   - Session logs (last 30 days)
   - Memory files
   - CLAUDE.md rules
   - memory-bridge shared data
   - claude.ai exports
   - **Real-time learning queue** (corrections, preferences, feedback captured by hooks)

2. **Validate** queued learnings first. For each item:
   - Is this a genuine reusable learning, or a one-time instruction?
   - Does it contradict any other queued item? If so, keep the more recent one.
   - Discard items that are context-specific and not generalizable.

3. Analyze ALL data. Validated queue items are highest-signal — weight them heavily.

   Extract patterns using this structure for EACH pattern:
   - **Pattern**: concise, actionable statement
   - **Evidence**: specific quote or behavior from the data
   - **Confidence**: high / medium / low

   Categories:
   - **Judgment** — decisions, accept/reject, risk tolerance, trade-offs, guardrails
   - **Style** — message length, tone, language, formatting, correction phrasing
   - **Priorities** — task types, delegation, recurring concerns, tools favored

   Aim for 8-15 patterns per category. Be specific, not generic.
   Check for contradictions between new and existing patterns.

4. Call `save_extracted_patterns()` with three markdown strings.

5. Call `generate_personal_skill()`. Pass the `role` argument if specified.

6. Show 5-8 most distinctive patterns. Ask if anything is wrong or missing.

Output: `skills/enhanced-self/SKILL.md`. Re-run anytime to update with new data.
