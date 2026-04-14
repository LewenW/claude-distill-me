# Plus-Me Development Conventions

## Code Style
- No obvious comments. Only comment WHY, never WHAT.
- Functions under 30 lines.
- Prefer flat over nested code.
- No dead code or TODOs without a reason.
- No filler words in strings or docs.

## Architecture
- Scanner collects raw data, never analyzes.
- Extractor prepares prompts and structures, Claude does the analysis.
- Generator merges patterns + role templates into SKILL.md.
- MCP server is a thin wrapper around scanner/extractor/generator.

## File Format
- All output is Markdown with YAML frontmatter.
- Frontmatter uses: name, description, type, tags.
- Memory files follow Claude Code auto-memory conventions.

## Testing
- Test with real session data from ~/.claude/projects/
- Verify generated SKILL.md loads correctly in Claude Code
