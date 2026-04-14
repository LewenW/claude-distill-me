# Plus-Me

**Distill your Claude data into a personal skill that makes Claude work like a more professional version of you.**

Plus-Me is a [Cowork](https://claude.ai/cowork) / Claude Code plugin that automatically learns your behavioral patterns from your Claude session history, memory files, and CLAUDE.md rules — then fuses them with industry best practices to generate a personal SKILL.md.

## What It Does

```
Your Claude Data          Pattern Extraction        Personal Skill
┌─────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Session logs     │      │ Judgment patterns │      │                  │
│ Memory files     │─────▶│ Communication    │─────▶│ enhanced-self/   │
│ CLAUDE.md rules  │      │ style            │      │ SKILL.md         │
│ Shared memories  │      │ Work priorities   │      │                  │
└─────────────────┘      └──────────────────┘      └──────────────────┘
         +                                                  +
  Role Templates ──────────────────────────────────────────▶│
  (PM, Engineering...)                              Best practices fused
```

**Not** a manual about-me config tool. Not a memory system. Not a colleague distiller.

Plus-Me reads your existing Claude data (no manual input needed) and learns *how you think* — your decision patterns, communication style, and work priorities.

## Quick Start

### Install as Cowork Plugin

```bash
# Clone the repo
git clone https://github.com/LewenW/claude-plus-me.git

# Install in Claude Code (from the plugin directory)
cd claude-plus-me
pip install -e .
```

Then add to your Claude Code settings or install via the plugin marketplace.

### Usage

```
/plus-me:distill        # Run full distillation (scan → extract → generate)
/plus-me:distill pm     # With PM best practices enhancement
/plus-me:profile        # View your current extracted patterns
```

## How It Works

1. **Scan** — Reads your `~/.claude/projects/` session logs (JSONL), memory files, and CLAUDE.md rules
2. **Extract** — Claude analyzes the data to identify your judgment patterns, communication style, and work priorities
3. **Fuse** — Merges your patterns with industry best practices (optional role template)
4. **Generate** — Outputs `skills/enhanced-self/SKILL.md` that auto-loads in future sessions

All processing is 100% local. No data leaves your machine.

## Architecture

```
claude-plus-me/
├── .claude-plugin/plugin.json     # Plugin manifest
├── .mcp.json                      # MCP server config
├── commands/
│   ├── distill.md                 # /plus-me:distill command
│   └── profile.md                 # /plus-me:profile command
├── skills/
│   ├── self-distill/SKILL.md      # Distillation guidance
│   └── enhanced-self/SKILL.md     # [Generated] Your personal skill
├── references/
│   └── role-templates/pm.md       # PM best practices
└── src/plus_me/
    ├── server.py                  # MCP server (4 tools)
    ├── scanner.py                 # Data collection
    ├── extractor.py               # Pattern extraction prompts
    └── generator.py               # SKILL.md generation
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `scan_user_data()` | Collect all local Claude data and prepare for analysis |
| `save_extracted_patterns()` | Save extracted judgment/style/priorities patterns |
| `generate_personal_skill()` | Generate SKILL.md from patterns + role template |
| `view_profile()` | View current extracted patterns |

## What Gets Extracted

### Judgment Patterns
How you make decisions: accept/reject Claude's suggestions, risk tolerance, quality standards, trade-off approaches.

### Communication Style
How you communicate: message length, language preferences (Chinese/English), tone, formatting, level of detail.

### Work Priorities
What you focus on: task types, delegation patterns, recurring themes, tools and frameworks you favor.

## Relationship to Memory-Bridge

Plus-Me is designed to work alongside [claude-memory-bridge](https://github.com/LewenW/claude-memory-bridge):

- **memory-bridge** = cross-project memory storage and retrieval
- **plus-me** = behavioral pattern distillation from that data (and more)

memory-bridge remembers *what you said*. Plus-Me learns *how you think*.

## Role Templates

MVP includes a PM (Product Manager) template. More coming:

- [ ] PM (available)
- [ ] Engineering
- [ ] Marketing
- [ ] Sales
- [ ] Legal
- [ ] Custom

## Roadmap

- [x] MVP: Manual `/distill` with session log + memory scanning
- [ ] Auto-evolution via SessionEnd hook
- [ ] claude.ai export data import
- [ ] Gmail/Calendar connector integration
- [ ] Multi-role template support
- [ ] Evolution log and pattern drift tracking
- [ ] Web dashboard for pattern visualization

## Privacy

- 100% local processing — zero network calls
- All data stays on your machine
- No telemetry, no cloud dependencies
- You can inspect every extracted pattern in `output/patterns/`

## Requirements

- Python 3.10+
- Claude Code or Cowork
- `mcp>=1.0.0`

## License

MIT
