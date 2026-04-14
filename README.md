# Plus-Me

Distill yourself into a SKILL.md. Learns your judgment, style, and priorities from Claude data.

Skills teach Claude how to do a type of work. Plus-Me teaches Claude how to do work **like you**.

> claude-reflect learns your tool preferences. colleague-skill distills your colleagues. Plus-Me distills **you** — your decision patterns, communication style, and priorities — then fuses them with industry best practices.

## How It Works

Two learning layers:

```
Real-time (automatic)                    On-demand (/distill)
─────────────────────                    ────────────────────
Every message you send                   Session logs + memories
  → hook detects corrections,            + queued learnings
    preferences, style signals           + claude.ai exports
  → queued as structured learnings         → deep pattern extraction
    with confidence scores                 → fused with role templates
                                           → SKILL.md output
```

All processing is local. No data leaves your machine.

## Install

```bash
git clone https://github.com/LewenW/claude-plus-me.git
cd claude-plus-me
pip install -e .

# Register MCP server
claude mcp add plus-me -e PYTHONPATH="$(pwd)/src" -- python -m plus_me.server
```

## Usage

```
/plus-me:distill        # synthesize all data → personal skill
/plus-me:distill pm     # same, with PM best practices fused in
/plus-me:profile        # view extracted patterns + queue stats
/plus-me:queue          # view captured learnings
/plus-me:import         # import claude.ai export data
```

Between `/distill` runs, hooks automatically capture corrections, preferences, and style signals from every message. These accumulate in a learning queue and feed into the next distill.

## What Gets Captured (Real-Time)

| Signal | Example | Confidence |
|--------|---------|:---:|
| Corrections | "no, use Python not JS" | 70-90% |
| Explicit markers | "remember: always use type hints" | 90% |
| Guardrails | "don't add comments unless I ask" | 85-90% |
| Style feedback | "too verbose, keep it short" | 80% |
| Preferences | "I prefer tables over lists" | 75% |
| Decisions | "let's go with option B" | 65-70% |
| Positive feedback | "perfect!" | 70% |

Repeated signals merge and boost confidence. Stale learnings decay and get pruned automatically.

## What Gets Extracted (/distill)

Three pattern categories, each with evidence and confidence:

- **Judgment** — decision-making, risk tolerance, trade-off approaches, guardrails
- **Style** — language, tone, formatting, message length, corrections
- **Priorities** — task types, delegation, recurring concerns, tools

<details>
<summary>Example generated SKILL.md (click to expand)</summary>

```markdown
## Decision-Making & Judgment

- When receiving a bug report, this user wants you to **verify each finding
  against current code first, then fix only real ones**.
  Evidence: "很多之前报的 bug 实际上已经在代码中处理了" — they value re-reading
  code over trusting the report.

- When choosing scope, this user **skips low-impact edge cases and only fixes
  functional + consistency issues**.
  Evidence: "Bug 1 和 Bug 3 值得修。其余都是极端边缘情况，不动。"

- When hitting ambiguity, this user **asks for the honest take, not an options
  menu**. Evidence: 多次问 "你觉得我这个做得好吗" — they want judgment, not
  the ball kicked back.

## Communication Style

- Primary language: Mandarin Chinese mixed with English technical terms.
  回复应同样中英混写.
- Short, casual, direct messages. Typical turns: "推"、"好啦"、"然后呢".
- Hates AI smell in code and docs. Banned words: "leverage", "utilize",
  "comprehensive", "robust", "seamless".
- Expects action, not clarifying questions. "帮我弄吧" means do it now.

## Work Priorities

- Building & shipping Claude ecosystem plugins is the active project line.
- GitHub discoverability / stars matter — actively researches naming,
  awesome-list submission, issue commenting.
- Quality bar: no AI-slop code, no filler comments, functions <30 lines,
  README readable in 60 seconds.
- Ship cadence is fast — same-day from spec to GitHub to PyPI.
```

</details>

## Data Sources

| Source | Location | When |
|--------|----------|------|
| Learning queue | `~/.claude/projects/*/plus-me-queue.json` | real-time |
| Session logs | `~/.claude/projects/*/*.jsonl` | on /distill |
| Memory files | `~/.claude/projects/*/memory/*.md` | on /distill |
| CLAUDE.md | `~/.claude/CLAUDE.md` + project-level | on /distill |
| memory-bridge | `~/.claude/shared-memory/` | on /distill |
| claude.ai exports | plugin `import/` directory | after /import |

## MCP Tools

| Tool | Purpose |
|------|---------|
| `scan_user_data()` | Collect all data + queue, return analysis prompts |
| `save_extracted_patterns()` | Write judgment/style/priorities to disk |
| `generate_personal_skill()` | Build SKILL.md from patterns + role template |
| `view_profile()` | Read patterns + queue stats |
| `view_queue()` | List captured learnings |

## Structure

```
├── hooks/hooks.json                    # UserPromptSubmit + Stop hooks
├── scripts/capture.py, session_end.py  # hook handlers
├── commands/distill, profile, queue, import
├── skills/self-distill/, enhanced-self/
├── references/role-templates/pm.md
└── src/plus_me/
    ├── server.py      # MCP server (5 tools)
    ├── scanner.py      # session/memory/export collection
    ├── extractor.py    # analysis prompt preparation
    ├── generator.py    # SKILL.md assembly
    └── queue.py        # learning queue + pattern detection
```

## Relation to memory-bridge

[memory-bridge](https://github.com/LewenW/claude-memory-bridge) stores and shares memories across projects. Plus-Me reads that data and goes further — it extracts behavioral patterns.

memory-bridge remembers what you said. Plus-Me learns how you think.

## Requirements

- Python 3.10+
- `mcp>=1.0.0`
- Claude Code or Cowork

## License

MIT
