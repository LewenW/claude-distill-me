"""Learning queue: structured storage for captured user signals."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from distill_me.config import CLAUDE_HOME


def _flock(lock_f, operation):
    """Cross-platform file locking. Uses fcntl on Unix, msvcrt on Windows."""
    try:
        import fcntl
        fcntl.flock(lock_f, operation)
    except ImportError:
        import msvcrt
        # msvcrt.locking needs at least 1 byte in the file to lock
        lock_f.write(" ")
        lock_f.flush()
        lock_f.seek(0)
        if operation in (1, 2):  # LOCK_SH, LOCK_EX
            msvcrt.locking(lock_f.fileno(), msvcrt.LK_LOCK, 1)
        else:  # LOCK_UN
            msvcrt.locking(lock_f.fileno(), msvcrt.LK_UNLCK, 1)


QUEUE_FILENAME = "distill-me-queue.json"


def _encode_project_dir(raw_path: str) -> str:
    """Encode a raw project path to match Claude Code's directory naming.

    Claude Code encodes /Users/bob/my-project as -Users-bob-my-project
    (replace / with -, keep leading dash, spaces become dashes too).
    """
    return raw_path.replace("/", "-").replace(" ", "-")


def _queue_path(project_dir: Optional[str] = None) -> Path:
    """Per-project queue at ~/.claude/projects/<encoded>/distill-me-queue.json.

    project_dir can be a raw path (from hooks, e.g. /Users/bob/myproject)
    or an already-encoded directory name (from scanning, e.g. -Users-bob-myproject).
    """
    if project_dir:
        if "/" in project_dir or "\\" in project_dir:
            encoded = _encode_project_dir(project_dir)
        else:
            encoded = project_dir
    else:
        encoded = "_global"
    path = CLAUDE_HOME / "projects" / encoded / QUEUE_FILENAME
    return path


@dataclass
class Learning:
    message: str
    learning_type: str  # correction, positive, explicit, preference, decision, style
    confidence: float
    extracted: str  # concise actionable statement
    timestamp: str = ""
    project: str = ""
    patterns: str = ""
    sentiment: str = "neutral"  # correction, positive, neutral
    decay_days: int = 90
    source: str = "hook"  # hook, session-analysis, distill


# --- Detection patterns ---
# Regex is a fast triage layer for English, Chinese, Japanese, Korean.
# /distill handles ALL languages via Claude's native understanding.

EXPLICIT_PATTERNS = [
    (r"remember:", "remember", 0.90, 120),
    (r"always\s+", "always", 0.80, 120),
    (r"never\s+", "never", 0.80, 120),
    (r"from now on", "from-now-on", 0.85, 120),
    (r"以后都", "yihou-dou", 0.85, 120),
    (r"记住", "jizhu", 0.90, 120),
    (r"今後は|これからは", "korekara", 0.85, 120),  # Japanese
    (r"앞으로는|기억해", "apeuroneun", 0.85, 120),  # Korean
]

CORRECTION_PATTERNS = [
    (r"^no[,. ]+", "no,", True),
    (r"^don't\b|^do not\b", "dont", True),
    (r"^stop\b|^never\b", "stop/never", True),
    (r"that's (wrong|incorrect)", "thats-wrong", True),
    (r"^actually[,. ]", "actually", False),
    (r"^I meant\b|^I said\b", "I-meant", True),
    (r"use .{1,30} not\b", "use-X-not-Y", True),
    # Chinese
    (r"^不是[，,. ]", "bushi", True),
    (r"^错了|^錯了", "cuole", True),
    (r"不要.{0,20}要", "buyao-yao", True),
    (r"^不对", "budui", True),
    (r"^别", "bie", True),
    (r"不是这样", "bushi-zheyang", True),
    # Japanese
    (r"^いや[、,. ]|^違う", "iya", True),
    (r"そうじゃなく", "souja-naku", True),
    # Korean
    (r"^아니[,. ]|^틀렸", "ani", True),
]

POSITIVE_PATTERNS = [
    (r"perfect!|exactly right", "perfect", 0.70, 90),
    (r"great approach|nailed it|excellent", "great", 0.70, 90),
    (r"好的|可以的|对的|没错", "hao-de", 0.65, 90),
    (r"就是这样|对对对", "jiushi-zheyang", 0.70, 90),
    (r"いいね|完璧|その通り", "iine", 0.70, 90),  # Japanese
    (r"좋아|맞아|완벽", "johah", 0.70, 90),  # Korean
    (r"👍|💯|🎯", "emoji-positive", 0.65, 90),
]

PREFERENCE_PATTERNS = [
    (r"I prefer\b|我喜欢|我偏好", "prefer", 0.75, 90),
    (r"I like\s+(to|it|when)|我觉得.{0,10}好", "like", 0.70, 90),
    (r"don't like|不喜欢|讨厌", "dislike", 0.75, 90),
]

STYLE_PATTERNS = [
    (r"(too|太)\s*(long|verbose|lengthy|啰嗦|冗长)", "too-long", 0.80, 90),
    (r"(too|太)\s*(short|brief|简单|简短)", "too-short", 0.80, 90),
    (r"(more|更)\s*(detail|具体|详细)", "more-detail", 0.75, 90),
    (r"(less|少)\s*(detail|废话)", "less-detail", 0.75, 90),
    (r"用中文|in Chinese|说中文", "use-chinese", 0.85, 120),
    (r"用英文|in English|说英文", "use-english", 0.85, 120),
]

GUARDRAIL_PATTERNS = [
    (r"don't (?:add|include|create) .{1,40} unless", "dont-unless-asked", 0.90, 120),
    (r"only (?:change|modify|edit) what I (?:asked|requested)", "only-what-asked", 0.90, 120),
    (r"don't .{1,30} without asking", "dont-without-asking", 0.85, 120),
    (r"(?:不要|别).{1,20}(?:除非|没说)", "buyao-chufei", 0.85, 120),
    (r"只(?:改|动|碰)我(?:说的|要求的)", "zhi-gai-woshuode", 0.90, 120),
]

DECISION_PATTERNS = [
    (r"let's go with\b|I('ll| will) go with", "go-with", 0.70, 60),
    (r"I chose\b|I('m| am) choosing", "chose", 0.70, 60),
    (r"我(选|决定用|选择)", "wo-xuan", 0.70, 60),
    (r"就.{0,6}吧", "jiu-yong-ba", 0.65, 60),
]

FALSE_POSITIVE_PATTERNS = [
    r"[?\uff1f]$",
    r"[\u55ce\u5417\u5462\u304b]$",  # 嗎吗呢か
    r"^(please|can you|could you|would you|help me)\b",
    r"^(ok|okay|好|行|はい|네)\s*$",
    r"^(yes|是的?|对|嗯|うん|응)\s*$",
]

MAX_CAPTURE_LENGTH = 500
MAX_WEAK_LENGTH = 150
MAX_QUEUE_SIZE = 200


def detect_learning(text: str) -> Optional[Learning]:
    """Detect if a user message contains a capturable learning signal."""
    stripped = text.strip()
    if not stripped:
        return None

    # Explicit markers always capture
    for pattern, name, confidence, decay in EXPLICIT_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return Learning(
                message=stripped,
                learning_type="explicit",
                confidence=confidence,
                extracted=stripped,
                patterns=name,
                sentiment="correction",
                decay_days=decay,
            )

    # Guardrail patterns (high signal — user setting boundaries)
    for pattern, name, confidence, decay in GUARDRAIL_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return Learning(
                message=stripped,
                learning_type="guardrail",
                confidence=confidence,
                extracted=stripped,
                patterns=name,
                sentiment="correction",
                decay_days=decay,
            )

    # False positive check
    for fp in FALSE_POSITIVE_PATTERNS:
        if re.search(fp, stripped, re.IGNORECASE):
            return None

    # Skip long messages (probably pasted content, not corrections)
    if len(stripped) > MAX_CAPTURE_LENGTH and "remember:" not in stripped.lower():
        return None

    # Style signals
    for pattern, name, confidence, decay in STYLE_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return Learning(
                message=stripped,
                learning_type="style",
                confidence=confidence,
                extracted=stripped,
                patterns=name,
                sentiment="correction",
                decay_days=decay,
            )

    # Preference signals
    for pattern, name, confidence, decay in PREFERENCE_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return Learning(
                message=stripped,
                learning_type="preference",
                confidence=confidence,
                extracted=stripped,
                patterns=name,
                sentiment="neutral",
                decay_days=decay,
            )

    # Positive feedback
    for pattern, name, confidence, decay in POSITIVE_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return Learning(
                message=stripped,
                learning_type="positive",
                confidence=confidence,
                extracted=stripped,
                patterns=name,
                sentiment="positive",
                decay_days=decay,
            )

    # Decision signals
    for pattern, name, confidence, decay in DECISION_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return Learning(
                message=stripped,
                learning_type="decision",
                confidence=confidence,
                extracted=stripped,
                patterns=name,
                sentiment="neutral",
                decay_days=decay,
            )

    # Correction patterns
    matched = []
    has_strong = False
    for pattern, name, is_strong in CORRECTION_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            if not is_strong and len(stripped) > MAX_WEAK_LENGTH:
                continue
            matched.append(name)
            if is_strong:
                has_strong = True

    if matched:
        if len(matched) >= 2:
            confidence = 0.80
        elif has_strong:
            confidence = 0.70
        else:
            confidence = 0.55

        # Short messages are more likely real corrections
        if len(stripped) < 80:
            confidence = min(0.90, confidence + 0.10)
        elif len(stripped) > 300:
            confidence = max(0.50, confidence - 0.15)

        return Learning(
            message=stripped,
            learning_type="correction",
            confidence=confidence,
            extracted=stripped,
            patterns=" ".join(matched),
            sentiment="correction",
            decay_days=90,
        )

    return None


def effective_confidence(item: dict) -> float:
    """Compute confidence adjusted for age and observation count.

    Repeated observations extend the effective decay period — a signal
    seen 5 times decays much slower than one seen once.
    """
    base = item.get("confidence", 0.5)
    decay_days = item.get("decay_days", 90)
    observations = item.get("observations", 1)
    ts = item.get("timestamp", "")
    if not ts or decay_days <= 0:
        return base
    try:
        created = datetime.fromisoformat(ts)
        age = (datetime.now(timezone.utc) - created).days
        adjusted_decay = decay_days * (1 + 0.3 * (observations - 1))
        if age >= adjusted_decay:
            return 0.0
        return base * (1 - age / adjusted_decay)
    except (ValueError, TypeError):
        return base


def _locked_read_write(path: Path, fn):
    """Read-modify-write with file lock to prevent race conditions.

    Cross-platform: uses fcntl on Unix, msvcrt on Windows.
    Logs to stderr on lock failure instead of silently dropping data.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_suffix(".lock")
    try:
        with open(lock_path, "w") as lock_f:
            _flock(lock_f, 2)  # LOCK_EX
            try:
                items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
            except (json.JSONDecodeError, OSError):
                items = []
            result = fn(items)
            path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
            return result
    except OSError as e:
        print(f"distill-me: lock failed for {path}: {e}", file=sys.stderr)
        return None


def load_queue(project_dir: Optional[str] = None) -> list[dict]:
    path = _queue_path(project_dir)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_queue(items: list[dict], project_dir: Optional[str] = None) -> None:
    path = _queue_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _is_duplicate(existing: dict, new: Learning) -> bool:
    """Check if new learning duplicates an existing one (same pattern + type)."""
    return (
        existing.get("patterns") == new.patterns
        and existing.get("learning_type") == new.learning_type
        and existing.get("patterns")  # empty patterns don't match
    )


def append_learning(learning: Learning, project_dir: Optional[str] = None) -> None:
    learning.timestamp = datetime.now(timezone.utc).isoformat()
    learning.project = project_dir or ""
    path = _queue_path(project_dir)

    def _append(items: list[dict]) -> None:
        for item in items:
            if _is_duplicate(item, learning):
                item["observations"] = item.get("observations", 1) + 1
                item["confidence"] = min(0.95, item["confidence"] + 0.05)
                item["timestamp"] = learning.timestamp
                item["message"] = learning.message
                return
        new_item = asdict(learning)
        new_item["observations"] = 1
        items.append(new_item)
        if len(items) > MAX_QUEUE_SIZE:
            items.sort(key=effective_confidence)
            del items[: len(items) - MAX_QUEUE_SIZE]

    _locked_read_write(path, _append)


def prune_stale(project_dir: Optional[str] = None) -> int:
    """Remove items whose confidence has decayed to zero. Returns count removed."""
    path = _queue_path(project_dir)
    removed = [0]

    def _prune(items: list[dict]) -> None:
        before = len(items)
        items[:] = [i for i in items if effective_confidence(i) > 0]
        removed[0] = before - len(items)

    _locked_read_write(path, _prune)
    return removed[0]


def queue_stats(project_dir: Optional[str] = None) -> dict:
    items = load_queue(project_dir)
    by_type: dict[str, int] = {}
    stale = 0
    for item in items:
        t = item.get("learning_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        if effective_confidence(item) <= 0:
            stale += 1
    return {"total": len(items), "by_type": by_type, "stale": stale}
