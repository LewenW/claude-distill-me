# Distill-Me

Distill yourself into a SKILL.md. Learns your judgment, style, and priorities from Claude data.

Skills teach Claude how to do a type of work. Distill-Me teaches Claude how to do work **like you**.

> Most memory tools capture "prefers tabs over spaces." Distill-Me captures "makes decisions by checking evidence before trusting reports, ships fast and iterates, handles ambiguity by demanding honest opinions, and their corrections reveal past bad experiences with over-helpful AI."

## How It Works

```
/distill-me:distill
```

One command. Scans your Claude sessions, memories, and rules. Extracts behavioral patterns at three depths:

```
Layer 1: Observable     — what you literally say and do
Layer 2: Interpretive   — what your patterns reveal about how you think
Layer 3: Contrastive    — what makes you DIFFERENT from most people
```

Output goes to `~/.claude/CLAUDE.md` (loads everywhere) and the plugin's `skills/enhanced-self/SKILL.md`.

Scanned data stays on disk. Analysis is done by Claude (via API), same as any Claude Code session.

## Install

```bash
git clone https://github.com/LewenW/claude-distill-me.git
cd claude-distill-me
pip install -e .

# Register MCP server
claude mcp add distill-me -e PYTHONPATH="$(pwd)/src" -- python -m distill_me.server
```

## Usage

```
/distill-me:distill        # extract patterns → personal skill
/distill-me:distill pm     # same, fused with PM best practices
```

## What Gets Extracted

Three categories, each with three-layer depth:

**Decision-Making & Cognitive Patterns**
- How you choose when presented with options
- Your implicit decision framework (evidence-driven? gut? speed-first?)
- Risk calibration and when it shifts by context
- What your guardrails reveal about past experiences
- What makes your reasoning different from most people

**Communication & Personality**
- Voice, language mixing patterns, message length as priority signal
- Your relationship with AI and how it shifts by task
- Emotional register — what triggers excitement, frustration, dismissal
- Gap between how you write and how you want Claude to write
- What makes your voice impossible to confuse with someone else's

**Values & Work Philosophy**
- Stated preferences vs revealed preferences (where they diverge)
- Values hierarchy — when two priorities conflict, which wins
- Root values driving surface decisions
- Meta-cognition: how you learn, handle your own mistakes

<details>
<summary>Example output (click to expand)</summary>

```markdown
## Decision-Making & Cognitive Patterns

- **Pattern**: When receiving external input (bug reports, reviews), this user
  verifies each claim against current code before acting — because they've been
  burned by trusting reports that were already handled.
  **Evidence**: "很多之前报的 bug 实际上已经在代码中处理了"
  **Depth**: interpretive

- **Pattern**: When scoping work, cuts aggressively — only fixes functional +
  consistency issues, skips low-impact edge cases. This isn't laziness; it's a
  trained instinct that scope creep kills shipping velocity.
  **Evidence**: "Bug 1 和 Bug 3 值得修。其余都是极端边缘情况，不动。"
  **Depth**: deep

## Communication & Personality

- **Pattern**: Uses 2-5 word commands for routine tasks ("推", "好啦", "帮我弄吧")
  but switches to detailed paragraphs when stakes are high. Message length IS
  the priority signal — short means "just do it", long means "think carefully."
  **Depth**: interpretive

- **Pattern**: Hates AI smell in output. Not just banned words ("leverage",
  "robust") — the underlying objection is to THINKING that produces generic,
  hedge-everything, please-everyone output. Wants opinionated, specific, direct.
  **Depth**: deep
```

</details>

## Role Fusion

Fuse your personal patterns with role-specific best practices:

```
/distill-me:distill pm                    # built-in PM template
/distill-me:distill discord/bot-builder   # from installed Cowork plugin
```

Two sources of roles:
1. **Built-in templates** — `references/role-templates/*.md` (ships with PM)
2. **Installed plugins** — any Cowork plugin in `~/.claude/plugins/` with a SKILL.md

Install a Cowork plugin, and its skills automatically become available as roles. Personal patterns always take priority — the role template adapts to fit you, not the reverse.

## Configuration

All limits are configurable via environment variables:

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `DISTILLME_SCAN_DAYS` | 30 | How many days of history to scan |
| `DISTILLME_MAX_SESSIONS` | 20 | Max session files to read |
| `DISTILLME_MAX_TOTAL_TURNS` | 100 | Max turns to collect |
| `DISTILLME_MAX_ANALYSIS_TURNS` | 80 | Turns sent to analysis |
| `DISTILLME_MAX_MESSAGE_CHARS` | 2000 | Per-message truncation |
| `DISTILLME_MAX_MEMORY_CHARS` | 1000 | Per-memory truncation |
| `DISTILLME_EXCLUDE_PROJECTS` | (none) | Comma-separated project names to skip |

Set them in your `.mcp.json` env block or shell profile.

## Data Sources

| Source | Location |
|--------|----------|
| Session logs | `~/.claude/projects/*/*.jsonl` |
| Memory files | `~/.claude/projects/*/memory/*.md` |
| CLAUDE.md | `~/.claude/CLAUDE.md` + project-level |
| memory-bridge | `~/.claude/shared-memory/` |

## MCP Tools

| Tool | Purpose |
|------|---------|
| `scan_user_data()` | Collect all data, return three-layer analysis prompts |
| `save_extracted_patterns()` | Write judgment/style/priorities to disk |
| `generate_personal_skill()` | Build SKILL.md from patterns + optional role fusion |

## Structure

```
├── commands/distill.md              # /distill-me:distill command
├── skills/
│   ├── self-distill/SKILL.md        # extraction quality guide
│   └── enhanced-self/SKILL.md       # [generated] your personal skill
├── references/role-templates/pm.md  # PM best practices
└── src/distill_me/
    ├── server.py                    # MCP server (3 tools)
    ├── scanner.py                   # data collection
    ├── extractor.py                 # three-layer extraction prompts
    └── generator.py                 # SKILL.md + CLAUDE.md injection
```

## Relation to memory-bridge

[memory-bridge](https://github.com/LewenW/claude-memory-bridge) stores and shares memories across projects. Distill-Me reads that data and goes further — it extracts behavioral patterns.

memory-bridge remembers what you said. Distill-Me learns how you think.

## Platform Compatibility

Works everywhere Claude loads `~/.claude/CLAUDE.md`:

| Feature | Claude Code CLI | Desktop | Cowork |
|---------|:-:|:-:|:-:|
| MCP tools | yes | yes | needs bridge |
| `/distill-me:distill` | yes | yes | yes |
| Output to CLAUDE.md | yes | yes | yes |

## Requirements

- Python 3.10+
- `mcp>=1.0.0`
- Claude Code (CLI or Desktop)

## License

MIT
