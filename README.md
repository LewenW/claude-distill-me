# Plus-Me

Cowork/Claude Code plugin that continuously learns your behavioral patterns and distills them into a personal SKILL.md.

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
| Style feedback | "太啰嗦了 简短一点" | 80% |
| Preferences | "I prefer tables over lists" | 75% |
| Positive feedback | "perfect!" / "就是这样" | 70% |

## What Gets Extracted (/distill)

Three pattern categories, each with evidence and confidence:

- **Judgment** — decision-making, risk tolerance, trade-off approaches
- **Style** — language, tone, formatting, message length, corrections
- **Priorities** — task types, delegation, recurring concerns, tools

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
