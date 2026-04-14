"""Scan ~/.claude for user data: session logs, memory files, CLAUDE.md."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from distill_me.config import (
    CLAUDE_MD_END,
    CLAUDE_MD_START,
    EXCLUDE_PROJECTS,
    GLOBAL_CLAUDE_MD,
    MAX_MESSAGE_CHARS,
    MAX_SESSIONS,
    MAX_TOTAL_TURNS,
    MAX_TURNS_PER_SESSION,
    PROJECTS_DIR,
    SCAN_DAYS,
    SHARED_MEMORY_DIR,
)


@dataclass
class Turn:
    user_message: str
    assistant_message: str
    session_id: str
    project: str
    timestamp: str = ""


@dataclass
class MemoryEntry:
    name: str
    description: str
    memory_type: str
    tags: list[str]
    content: str
    source_path: str


@dataclass
class UserData:
    turns: list[Turn] = field(default_factory=list)
    memories: list[MemoryEntry] = field(default_factory=list)
    claude_md_rules: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SYSTEM_REMINDER_RE = re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL)

# Common parent dirs for decoding encoded project paths
_PATH_MARKERS = (
    "-Desktop-", "-Documents-", "-repos-", "-Projects-",
    "-projects-", "-code-", "-src-", "-workspace-", "-work-",
)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta, text[m.end():]


def _truncate(s: str, limit: int = MAX_MESSAGE_CHARS) -> str:
    if len(s) <= limit:
        return s
    return s[:limit] + "..."


def _is_tool_message(content) -> bool:
    """Check if message content is tool results/calls, not real user input."""
    if not isinstance(content, list):
        return False
    return any(
        isinstance(b, dict) and b.get("type") in ("tool_result", "tool_use")
        for b in content
    )


def _extract_text(content) -> str:
    """Extract readable text from message content blocks.

    Tool_use/tool_result blocks collapse to a count.
    System-reminder tags are stripped.
    """
    if isinstance(content, str):
        return _SYSTEM_REMINDER_RE.sub("", content)
    if isinstance(content, list):
        parts = []
        tool_count = 0
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif not isinstance(block, dict):
                continue
            elif block.get("type") == "text":
                text = block.get("text", "")
                text = _SYSTEM_REMINDER_RE.sub("", text)
                if text.strip():
                    parts.append(text)
            elif block.get("type") in ("tool_use", "tool_result"):
                tool_count += 1
        if tool_count:
            parts.append(f"[used {tool_count} tools]")
        return "\n".join(parts)
    return str(content)


def _strip_distill_section(text: str) -> str:
    """Remove distill-me's own output to prevent feedback loops on re-distill."""
    start = text.find(CLAUDE_MD_START)
    end = text.find(CLAUDE_MD_END)
    if start != -1 and end != -1 and start < end:
        return text[:start] + text[end + len(CLAUDE_MD_END):]
    return text


def _is_excluded(dir_name: str) -> bool:
    if not EXCLUDE_PROJECTS:
        return False
    return dir_name in EXCLUDE_PROJECTS


def _decode_project_name(encoded: str) -> str:
    """Extract project name from encoded directory path.

    -Users-bob-Desktop-my-project → my-project
    -home-user-work-api → api
    """
    for marker in _PATH_MARKERS:
        idx = encoded.rfind(marker)
        if idx != -1:
            return encoded[idx + len(marker):]
    return encoded


class DataScanner:

    def scan_sessions(self) -> list[Turn]:
        if not PROJECTS_DIR.exists():
            return []

        cutoff = time.time() - (SCAN_DAYS * 86400)
        session_files: list[tuple[float, Path, str]] = []

        for proj_dir in PROJECTS_DIR.iterdir():
            if not proj_dir.is_dir():
                continue
            if _is_excluded(proj_dir.name):
                continue
            for f in proj_dir.glob("*.jsonl"):
                try:
                    mtime = f.stat().st_mtime
                except OSError:
                    continue
                if mtime >= cutoff:
                    session_files.append((mtime, f, proj_dir.name))

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
        turns: list[Turn] = []
        pending_user: dict | None = None
        session_id = fpath.stem
        readable_project = _decode_project_name(proj_name)

        try:
            with open(fpath, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Skip subagent conversations
                    if event.get("isSidechain"):
                        continue

                    evt_type = event.get("type")
                    msg = event.get("message", {})

                    if evt_type == "user" and msg.get("role") == "user":
                        content = msg.get("content", "")
                        # Skip tool result events masquerading as user messages
                        if _is_tool_message(content):
                            continue
                        text = _extract_text(content)
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
                                project=readable_project,
                                timestamp=pending_user["timestamp"],
                            ))
                            pending_user = None

                    if len(turns) >= MAX_TURNS_PER_SESSION:
                        break
        except (OSError, PermissionError, UnicodeDecodeError):
            pass

        return turns

    def scan_memories(self) -> list[MemoryEntry]:
        if not PROJECTS_DIR.exists():
            return []

        entries: list[MemoryEntry] = []
        for proj_dir in PROJECTS_DIR.iterdir():
            if _is_excluded(proj_dir.name):
                continue
            mem_dir = proj_dir / "memory"
            if not mem_dir.is_dir():
                continue
            for md_file in mem_dir.glob("*.md"):
                if md_file.name == "MEMORY.md":
                    continue
                entry = self._parse_memory(md_file)
                if entry:
                    entries.append(entry)

        return entries

    def scan_memory_bridge(self) -> list[MemoryEntry]:
        if not SHARED_MEMORY_DIR.exists():
            return []

        entries: list[MemoryEntry] = []
        for ns_dir in SHARED_MEMORY_DIR.iterdir():
            if not ns_dir.is_dir():
                continue
            if _is_excluded(ns_dir.name):
                continue
            for md_file in ns_dir.glob("*.md"):
                if md_file.name == "MEMORY.md":
                    continue
                entry = self._parse_memory(md_file)
                if entry:
                    entries.append(entry)

        return entries

    def scan_claude_md(self) -> list[str]:
        rules: list[str] = []

        if GLOBAL_CLAUDE_MD.exists():
            try:
                text = GLOBAL_CLAUDE_MD.read_text(encoding="utf-8")
                text = _strip_distill_section(text)
                if text.strip():
                    rules.append(f"[Global CLAUDE.md]\n{text.strip()}")
            except OSError:
                pass

        if PROJECTS_DIR.exists():
            for proj_dir in PROJECTS_DIR.iterdir():
                if _is_excluded(proj_dir.name):
                    continue
                claude_md = proj_dir / "CLAUDE.md"
                if claude_md.exists():
                    try:
                        text = claude_md.read_text(encoding="utf-8")
                        if text.strip():
                            proj_label = _decode_project_name(proj_dir.name)
                            rules.append(f"[{proj_label}/CLAUDE.md]\n{text.strip()}")
                    except OSError:
                        pass

        return rules

    def _parse_memory(self, fpath: Path) -> MemoryEntry | None:
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

    def collect_all(self) -> UserData:
        turns = self.scan_sessions()
        memories = self.scan_memories()
        bridge_memories = self.scan_memory_bridge()
        rules = self.scan_claude_md()

        all_memories = memories + bridge_memories
        projects = {t.project for t in turns}
        sessions = {t.session_id for t in turns}

        return UserData(
            turns=turns,
            memories=all_memories,
            claude_md_rules=rules,
            stats={
                "total_turns": len(turns),
                "total_memories": len(all_memories),
                "project_memories": len(memories),
                "bridge_memories": len(bridge_memories),
                "total_rules": len(rules),
                "projects_scanned": len(projects),
                "sessions_scanned": len(sessions),
            },
        )
