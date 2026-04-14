---
name: distill
description: Scan your Claude data and distill your behavioral patterns into a personal skill
argument-hint: "[role]"
---

# Plus-Me: Distill Your Personal Skill

Run the full distillation pipeline to create a personal skill from your Claude data.

## Steps

1. **Scan**: Call `scan_user_data()` to collect all local Claude data (session logs, memory files, CLAUDE.md rules).

2. **Analyze**: Read through the scan results carefully. Extract three types of patterns from the data:
   - **Judgment patterns**: How the user makes decisions, evaluates options, accepts/rejects suggestions
   - **Communication style**: Message length, tone, language, formatting preferences
   - **Work priorities**: What they focus on, delegate, skip, and care about

   For each pattern, cite specific evidence from the data. Be specific, not generic.

3. **Save**: Call `save_extracted_patterns()` with the three pattern sections as markdown strings.

4. **Generate**: Call `generate_personal_skill()` to create the final SKILL.md.
   - If the user specified a role (e.g. "pm"), pass it as the `role` parameter
   - Otherwise, generate a pure pattern-based skill

5. **Report**: Show the user a summary of what was learned. Highlight 3-5 most distinctive patterns. Ask if anything feels off or missing.

## Notes

- The generated skill will be saved to `skills/enhanced-self/SKILL.md` and auto-loads in future sessions.
- First run may take a minute to scan all data.
- User can re-run to update patterns as more data accumulates.
