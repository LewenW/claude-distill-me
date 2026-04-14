# Distill-Me Development Rules

## Code Style

- No obvious comments. Only comment WHY, never WHAT.
- No filler words in comments: no "basically", "simply", "just", "essentially", "Note that".
- Variable and function names should be self-documenting. If you need a comment to explain what code does, rename instead.
- Prefer flat over nested. Early return over deep if/else.
- Functions under 30 lines. If longer, extract.
- No dead code, no commented-out code, no TODO without a reason.

## README Style

- First line: what this project does in one sentence. No adjectives.
- Then: install, usage, done. Respect the reader's time.
- No "Welcome to...", no "This project aims to...", no "Getting Started" as a section name when you mean "Install".
- No badges unless they convey real info (build status yes, "made with love" no).
- Code examples over prose. Show, don't describe.
- Write for someone who has 60 seconds to decide if this is useful.

## Writing Tone

- Direct. Short sentences. No filler.
- Never use: "leverage", "utilize", "comprehensive", "robust", "seamless", "cutting-edge", "empower".
- Prefer "use" over "utilize", "complete" over "comprehensive", "works with" over "seamlessly integrates".

## Architecture

- Scanner collects raw data, never analyzes.
- Extractor prepares prompts and data for Claude. It does NOT extract patterns itself.
- Generator merges patterns + role templates into SKILL.md.
- MCP server is a thin wrapper around scanner/extractor/generator.
- All output is Markdown with YAML frontmatter.
