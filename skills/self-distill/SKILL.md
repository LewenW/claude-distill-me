---
name: self-distill
description: Guides the Plus-Me distillation process. Activates when the user wants to create or update their personal skill, or when Plus-Me tools are used.
version: 0.1.0
---

# Plus-Me Self-Distillation Guide

You have access to Plus-Me, a tool that distills the user's behavioral patterns from their Claude data.

## When to Suggest Distillation

- The user asks you to "learn" them or "understand" their style
- The user wants a personal skill or personalized agent
- The user mentions Plus-Me or pattern extraction
- The user asks "how do I usually do X?" (suggest distilling first if no profile exists)

## Pattern Extraction Guidelines

When analyzing user data from `scan_user_data()`, extract patterns that are:

1. **Specific**: "User prefers 3-bullet summaries over paragraphs" not "user likes brevity"
2. **Evidence-backed**: Always tie patterns to observed behavior in the data
3. **Actionable**: Each pattern should guide how Claude should behave differently
4. **Distinctive**: Focus on what makes this user unique, not universal preferences

### Judgment Patterns to Look For
- Accept/reject ratio for Claude's suggestions
- How they handle ambiguity (ask for clarity vs make assumptions)
- Risk tolerance (conservative vs aggressive approaches)
- Quality vs speed trade-offs

### Style Patterns to Look For
- Language: Chinese, English, or code-switching patterns
- Message structure: short commands vs detailed briefs
- Formatting: use of markdown, lists, headers, code blocks
- Tone: formal, casual, technical, conversational

### Priority Patterns to Look For
- Task types they initiate most often
- What they correct or push back on
- What they skip or accept without review
- Recurring themes across sessions

## After Distillation

Let the user review the generated patterns and skill. Be open to corrections — user corrections are the highest-quality signal for improving accuracy.
