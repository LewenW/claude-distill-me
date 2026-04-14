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

2. Analyze ALL data. The queued learnings are high-signal — weight them heavily.

   Extract patterns using this structure for EACH pattern:
   - **Pattern**: concise, actionable statement
   - **Evidence**: specific quote or behavior from the data
   - **Confidence**: high / medium / low

   Three categories:
   - **Judgment** — decisions, accept/reject, risk tolerance, trade-offs
   - **Style** — message length, tone, language, formatting, correction phrasing
   - **Priorities** — task types, delegation, recurring concerns, tools favored

   Aim for 8-15 patterns per category. Be specific, not generic.

3. Call `save_extracted_patterns()` with three markdown strings.

4. Call `generate_personal_skill()`. Pass the `role` argument if specified.

5. Show 5-8 most distinctive patterns. Ask if anything is wrong or missing.

Output: `skills/enhanced-self/SKILL.md`. Re-run anytime to update with new data.
