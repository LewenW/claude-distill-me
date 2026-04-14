---
name: distill
description: Scan your Claude data and distill behavioral patterns into a personal skill
argument-hint: "[role]"
---

# Distill

Run the full pipeline: scan → extract → generate.

## Steps

1. Call `scan_user_data()`. This collects session logs, memory files, CLAUDE.md, memory-bridge data, and claude.ai exports.

2. Analyze the returned data. Extract three pattern types:
   - **Judgment** — decisions, accept/reject patterns, risk tolerance, trade-offs
   - **Style** — message length, tone, language, formatting, correction phrasing
   - **Priorities** — task types, delegation, recurring concerns, tools favored

   Cite evidence. Be specific, not generic. "Prefers 3-bullet summaries" beats "likes brevity".

3. Call `save_extracted_patterns()` with three markdown strings.

4. Call `generate_personal_skill()`. Pass the `role` argument if the user specified one (e.g. "pm").

5. Show the user 3-5 most distinctive patterns found. Ask if anything is wrong or missing.

Output lands in `skills/enhanced-self/SKILL.md`. Re-run anytime to update.
