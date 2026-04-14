# Plus-Me

Cowork/Claude Code plugin that distills your behavioral patterns from Claude data into a personal SKILL.md.

## What It Does

Scans your local Claude data (session logs, memory files, CLAUDE.md, memory-bridge namespaces, claude.ai exports). Extracts how you make decisions, communicate, and prioritize. Optionally fuses with role-specific best practices (PM, etc.). Outputs a `SKILL.md` that auto-loads in future sessions.

```
~/.claude data  →  scan  →  pattern extraction  →  SKILL.md
                                                      +
                              role templates  ────────┘
```

All processing is local. No data leaves your machine.

## Install

```bash
git clone https://github.com/LewenW/claude-plus-me.git
cd claude-plus-me
pip install -e .
```

## Usage

```bash
/plus-me:distill        # scan → extract patterns → generate skill
/plus-me:distill pm     # same, with PM best practices fused in
/plus-me:profile        # view extracted patterns
/plus-me:import         # import claude.ai exported data
```

## Data Sources

| Source | Location | Auto-scanned |
|--------|----------|:---:|
| Session logs | `~/.claude/projects/*/*.jsonl` | yes |
| Memory files | `~/.claude/projects/*/memory/*.md` | yes |
| CLAUDE.md | `~/.claude/CLAUDE.md` + project-level | yes |
| memory-bridge | `~/.claude/shared-memory/` | yes |
| claude.ai exports | plugin `import/` directory | after `/import` |

For richer patterns (especially new users with few sessions), export your claude.ai data:
Settings → Export Data → place JSON files in the `import/` directory.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `scan_user_data()` | Collect data, return analysis prompts |
| `save_extracted_patterns()` | Write judgment/style/priorities to disk |
| `generate_personal_skill()` | Build SKILL.md from patterns + role template |
| `view_profile()` | Read current patterns |

## How It Works

1. **Scanner** reads `~/.claude` — session JSONL, memory markdown, CLAUDE.md, memory-bridge namespaces, claude.ai exports
2. **Extractor** prepares data summaries and analysis prompts
3. **Claude** analyzes the data inline (no separate ML model)
4. **Generator** merges extracted patterns with role templates into a SKILL.md

The extractor prepares; Claude analyzes; the generator assembles.

## Extracted Patterns

Three categories:

- **Judgment** — decision-making, risk tolerance, trade-off approaches, accept/reject patterns
- **Style** — message length, language, tone, formatting, correction phrasing
- **Priorities** — task types, delegation patterns, recurring concerns, tools favored

## Relation to memory-bridge

[memory-bridge](https://github.com/LewenW/claude-memory-bridge) stores and shares memories across projects. Plus-Me reads that data and goes further — it extracts *behavioral patterns* from it.

memory-bridge remembers what you said. Plus-Me learns how you think.

## Structure

```
├── commands/distill.md, profile.md, import.md
├── skills/self-distill/, enhanced-self/
├── references/role-templates/pm.md
└── src/plus_me/
    ├── server.py       # MCP server (4 tools)
    ├── scanner.py       # data collection
    ├── extractor.py     # prompt preparation
    └── generator.py     # SKILL.md assembly
```

## Requirements

- Python 3.10+
- `mcp>=1.0.0`
- Claude Code or Cowork

## License

MIT
