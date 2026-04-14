"""Scan ~/.claude for user data: session logs, memory files, CLAUDE.md."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from plus_me.config import (
    CLAUDE_HOME,
    GLOBAL_CLAUDE_MD,
    MAX_MESSAGE_CHARS,
    MAX_SESSIONS,
    MAX_TOTAL_TURNS,
    MAX_TURNS_PER_SESSION,
    PROJECTS_DIR,
    SHARED_MEMORY_DIR,
)


@dataclass
class Turn:
    """A single user-assistant conversation turn."""
    user_message: str
    assistant_message: str
    session_id: str
    project: str
    timestamp: str = ""


@dataclass
class MemoryEntry:
    """A parsed memory file."""
    name: str
    description: str
    memory_type: str
    tags: list[str]
    content: str
    source_path: str


@dataclass
class UserData:
    """All collected user data from Claude ecosystem."""
    turns: list[Turn] = field(default_factory=list)
    memories: list[MemoryEntry] = field(default_factory=list)
    claude_md_rules: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


_FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML-like frontmatter and body from markdown."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    body = text[m.end():]
    return meta, body


def _truncate(s: str, limit: int = MAX_MESSAGE_CHARS) -> str:
    return s[:limit] + "..." if len(s) > limit else s


def _extract_text(content) -> str:
    """Extract plain text from message content (string or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") == "thinking":
                    pass  # skip internal reasoning
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


class DataScanner:
    """Collects user data from the local Claude ecosystem."""

    def scan_sessions(self) -> list[Turn]:
        """Read JSONL session files and extract conversation turns."""
        if not PROJECTS_DIR.exists():
            return []

        session_files: list[tuple[float, Path, str]] = []
        for proj_dir in PROJECTS_DIR.iterdir():
            if not proj_dir.is_dir():
                continue
            proj_name = proj_dir.name
            for f in proj_dir.glob("*.jsonl"):
                session_files.append((f.stat().st_mtime, f, proj_name))

        # Most recent sessions first
        session_files.sort(key=lambda x: x[0], reverse=True)
        session_files = session_files[:MAX_SESSIONS]

        all_turns: list[Turn] = []
        for _, fpath, proj_name in session_files:
            turns = self._parse_session(fpath, proj_name)
            all_turns.extend(turns)
            if len(all_turns) >= MAX_TOTAL_TURNS:
                break

        return all_turns[:MAX_TOTAL_TURNS]

    def _parse_session(self, fpath: Path, proj_name: str) -> list[Turn]:
        """Parse a single JSONL session file into turns."""
        turns: list[Turn] = []
        pending_user: dict | None = None
        session_id = fpath.stem

        try:
            with open(fpath) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    evt_type = event.get("type")
                    msg = event.get("message", {})

                    if evt_type == "user" and msg.get("role") == "user":
                        text = _extract_text(msg.get("content", ""))
                        if text.strip():
                            pending_user = {
                                "text": text,
                                "timestamp": event.get("timestamp", ""),
                            }

                    elif evt_type == "assistant" and msg.get("role") == "assistant" and pending_user:
                        text = _extract_text(msg.get("content", ""))
                        if text.strip():
                            turns.append(Turn(
                                user_message=_truncate(pending_user["text"]),
                                assistant_message=_truncate(text),
                                session_id=session_id,
                                project=proj_name,
                                timestamp=pending_user["timestamp"],
                            ))
                            pending_user = None

                    if len(turns) >= MAX_TURNS_PER_SESSION:
                        break
        except (OSError, PermissionError):
            pass

        return turns

    def scan_memories(self) -> list[MemoryEntry]:
        """Read memory/*.md files across all projects."""
        if not PROJECTS_DIR.exists():
            return []

        entries: list[MemoryEntry] = []
        for proj_dir in PROJECTS_DIR.iterdir():
            mem_dir = proj_dir / "memory"
            if not mem_dir.is_dir():
                continue
            for md_file in mem_dir.glob("*.md"):
                if md_file.name == "MEMORY.md":
                    continue  # skip index
                entry = self._parse_memory(md_file)
                if entry:
                    entries.append(entry)

        # Also scan shared memory
        if SHARED_MEMORY_DIR.exists():
            for ns_dir in SHARED_MEMORY_DIR.iterdir():
                if not ns_dir.is_dir():
                    continue
                for md_file in ns_dir.glob("*.md"):
                    if md_file.name == "MEMORY.md":
                        continue
                    entry = self._parse_memory(md_file)
                    if entry:
                        entries.append(entry)

        return entries

    def _parse_memory(self, fpath: Path) -> MemoryEntry | None:
        """Parse a single memory markdown file."""
        try:
            text = fpath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

        meta, body = _parse_frontmatter(text)
        if not body.strip():
            return None

        tags_str = meta.get("tags", "")
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        return MemoryEntry(
            name=meta.get("name", fpath.stem),
            description=meta.get("description", ""),
            memory_type=meta.get("type", "unknown"),
            tags=tags,
            content=body.strip(),
            source_path=str(fpath),
        )

    def scan_claude_md(self) -> list[str]:
        """Read global and project-level CLAUDE.md files."""
        rules: list[str] = []

        # Global CLAUDE.md
        if GLOBAL_CLAUDE_MD.exists():
            try:
                text = GLOBAL_CLAUDE_MD.read_text(encoding="utf-8")
                if text.strip():
                    rules.append(f"[Global CLAUDE.md]\n{text.strip()}")
            except OSError:
                pass

        # Project-level CLAUDE.md files
        if PROJECTS_DIR.exists():
            for proj_dir in PROJECTS_DIR.iterdir():
                claude_md = proj_dir / "CLAUDE.md"
                if claude_md.exists():
                    try:
                        text = claude_md.read_text(encoding="utf-8")
                        if text.strip():
                            rules.append(f"[{proj_dir.name}/CLAUDE.md]\n{text.strip()}")
                    except OSError:
                        pass

        return rules

    def collect_all(self) -> UserData:
        """Run all scanners and return combined user data."""
        turns = self.scan_sessions()
        memories = self.scan_memories()
        rules = self.scan_claude_md()

        projects = {t.project for t in turns}
        sessions = {t.session_id for t in turns}

        return UserData(
            turns=turns,
            memories=memories,
            claude_md_rules=rules,
            stats={
                "total_turns": len(turns),
                "total_memories": len(memories),
                "total_rules": len(rules),
                "projects_scanned": len(projects),
                "sessions_scanned": len(sessions),
            },
        )
