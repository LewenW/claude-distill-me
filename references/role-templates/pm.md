# Product Manager Best Practices

Sources: Marty Cagan (SVPG/Inspired), Teresa Torres (Continuous Discovery), Lenny Rachitsky, RICE/ICE frameworks, Shape Up (Basecamp).

## Prioritization

Use RICE when comparing items across a backlog:
- Reach: how many users affected per quarter
- Impact: scored 0.25 / 0.5 / 1 / 2 / 3
- Confidence: percentage based on evidence quality
- Effort: person-months

Use ICE for quick triage: Impact x Confidence x Ease, each 1-10.

MoSCoW for scope: Must / Should / Could / Won't. Define "Must" as "launch is pointless without this."

When two items score similarly, pick the one that unblocks more future work.

## Problem Definition

Start every feature with a problem statement, not a solution. Format:

> [User segment] needs [capability] because [evidence]. Today they [current workaround]. Success = [measurable outcome].

Validate the problem before designing the solution. Use Teresa Torres' opportunity solution tree: map opportunities (user needs) separately from solutions. Interview at least 5 users before committing to a direction.

## PRD Structure

1. Problem statement (who, what, why, evidence)
2. Success metrics with targets and timeline
3. Scope: what's in, what's out (explicit both)
4. User stories: "As [role], I want [action] so that [benefit]"
5. Technical constraints and dependencies
6. Launch criteria: go/no-go checklist
7. Risks and mitigations

No PRD should exceed 3 pages for v1. If it's longer, the scope is too big.

## Stakeholder Communication

Lead with the recommendation, then reasoning. Never present a problem without a proposed path.

For executives: one paragraph, one metric, one ask.
For engineers: context on user need, constraints, non-goals.
For design: user quotes, behavioral data, success criteria.

Frame trade-offs explicitly: "Option A ships in 2 weeks with X limitation. Option B ships in 6 weeks without it. I recommend A because [reason]."

## Execution

Ship incrementally. First version should be embarrassingly small.

Define "done" before starting. Acceptance criteria, not vibes.

Run pre-mortems: "It's 3 months from now and this failed. Why?" Write down the top 3 reasons and mitigate them.

Track leading indicators weekly. Lagging indicators monthly. If leading indicators don't move after 2 sprints, re-evaluate.

Say no by default. Every yes has an opportunity cost. Make that cost explicit.

## Discovery

Continuous discovery over big-bang research. Weekly user touchpoints, not quarterly studies.

Assumption mapping: list assumptions, rank by risk (impact if wrong x uncertainty), test highest-risk first.

Prototype to learn, not to ship. Fidelity should match the question being answered.

## Communication Templates

Status update: Progress / Blockers / Next Steps / Asks
Decision request: Context / Options (max 3) / Recommendation / Deadline
Feature brief: Problem / Solution / Metrics / Scope / Timeline
Retrospective: What worked / What didn't / Action items with owners
