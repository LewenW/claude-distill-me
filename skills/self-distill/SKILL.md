---
name: self-distill
description: Guides Plus-Me distillation. Activates when user wants to create or update their personal skill, or when Plus-Me tools are used.
version: 0.1.0
---

# Self-Distillation Guide

## When to Suggest

- User asks to "learn me" or "understand my style"
- User wants a personal skill or personalized agent
- User mentions Plus-Me or pattern extraction
- User asks "how do I usually do X" (suggest distilling first if no profile exists)

## Extraction Quality

When analyzing `scan_user_data()` output, extract patterns that are:

- **Specific**: "Prefers 3-bullet summaries over paragraphs" not "likes brevity"
- **Evidence-backed**: Tie each pattern to observed behavior
- **Actionable**: Each pattern should change Claude's output
- **Distinctive**: What makes this user different, not universal preferences

### Judgment — look for:
- Accept/reject ratio on suggestions
- Ambiguity handling (asks vs assumes)
- Risk tolerance (conservative vs aggressive)
- Quality vs speed trade-offs

### Style — look for:
- Language: Chinese, English, or code-switching
- Structure: short commands vs detailed briefs
- Formatting: markdown, lists, headers, code blocks
- Tone: formal, casual, technical

### Priorities — look for:
- Task types initiated most often
- What gets corrected or pushed back on
- What gets skipped or accepted without review
- Recurring themes across sessions

## After Distillation

Let the user review. User corrections are the highest-quality signal.
