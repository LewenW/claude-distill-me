---
name: self-distill
description: Guides deep behavioral distillation — three-layer extraction of decision patterns, personality, and values.
---

# Deep Distillation Guide

## Three-Layer Extraction

Every pattern category uses the same depth progression:

**Layer 1 — Observable:** Direct evidence from the data. What did they literally say or do?
**Layer 2 — Interpretive:** What do the patterns imply? Read between the lines.
**Layer 3 — Contrastive:** What makes this person DIFFERENT? What would surprise you?

## Extraction Quality Standards

Each pattern MUST have:
- **Pattern**: When [situation], this user [behavior] because [underlying reason]
- **Evidence**: specific quote or concrete behavior from the data
- **Confidence**: high / medium / low
- **Depth**: surface / interpretive / deep

Bad pattern: "Prefers short messages"
Good pattern: "Uses 2-5 word commands for routine tasks but switches to detailed paragraphs when stakes are high — the message length IS the priority signal"

Bad pattern: "Uses Chinese and English"
Good pattern: "Thinks in Chinese but keeps technical terms in English. Code-switches mid-sentence. The ratio of Chinese to English tracks their emotional engagement — more Chinese = more invested"

## Decision-Making — Look For:
- Accept/reject patterns on AI suggestions
- Implicit decision frameworks (data-driven? gut? speed-first?)
- How they handle ambiguity (ask vs assume vs demand opinion)
- Risk calibration (ship fast vs polish) and when it shifts
- Guardrails and what past experiences they reveal
- Trust architecture: what triggers verification vs delegation?

## Communication — Look For:
- Message length as a function of context (not just "short" or "long")
- Language mixing rules (which language for what, and why)
- Relationship with AI (peer? tool? how does this shift?)
- Emotional register triggers (excitement, frustration, dismissal)
- What they HATE in output and what that hatred reveals
- Gap between their own style and their expectations for AI output

## Values — Look For:
- Revealed preferences vs stated preferences (where they diverge)
- What they spend attention on that most people in their role wouldn't
- What they skip that most people wouldn't skip
- Values hierarchy: when two priorities conflict, which wins?
- Root values driving surface decisions (usually 1-2 core values)
- Meta-cognition: how they learn, handle their own mistakes

## After Extraction

User corrections to generated patterns are the highest-quality signal. If they say "that's wrong" or "that's not why", the correction reveals more about them than the original data did. Incorporate immediately.
