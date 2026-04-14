"""Learning queue: structured storage for captured user signals."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from plus_me.config import CLAUDE_HOME


def _queue_path(project_dir: Optional[str] = None) -> Path:
    """Per-project queue at ~/.claude/projects/<encoded>/plus-me-queue.json."""
    if project_dir:
        encoded = project_dir.replace("/", "-").lstrip("-")
    else:
        encoded = "_global"
    path = CLAUDE_HOME / "projects" / encoded / "plus-me-queue.json"
    path.parent.mkdir(parents=True, exist_ok=True)
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

EXPLICIT_PATTERNS = [
    (r"remember:", "remember", 0.90, 120),
    (r"always\s+", "always", 0.80, 120),
    (r"never\s+", "never", 0.80, 120),
    (r"from now on", "from-now-on", 0.85, 120),
    (r"以后都", "yihou-dou", 0.85, 120),
    (r"记住", "jizhu", 0.90, 120),
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
]

POSITIVE_PATTERNS = [
    (r"perfect!|exactly right", "perfect", 0.70, 90),
    (r"great approach|nailed it|excellent", "great", 0.70, 90),
    (r"好的|可以的|对的|没错", "hao-de", 0.65, 90),
    (r"就是这样|对对对", "jiushi-zheyang", 0.70, 90),
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
    r"[\u55ce\u5417\u5462]$",  # 嗎吗呢
    r"^(please|can you|could you|would you|help me)\b",
    r"^(ok|okay|好|行)\s*$",
    r"^(yes|是的?|对|嗯)\s*$",
]

MAX_CAPTURE_LENGTH = 500
MAX_WEAK_LENGTH = 150
MAX_QUEUE_SIZE = 200


def detect_learning(text: str) -> Optional[Learning]:
    """Detect if a user message contains a capturable learning signal."""
    stripped = text.strip()
    if len(stripped) <= 1:
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
    """Compute confidence adjusted for age. Items decay toward 0 over decay_days."""
    base = item.get("confidence", 0.5)
    decay_days = item.get("decay_days", 90)
    ts = item.get("timestamp", "")
    if not ts or decay_days <= 0:
        return base
    try:
        created = datetime.fromisoformat(ts)
        age = (datetime.now(timezone.utc) - created).days
        if age >= decay_days:
            return 0.0
        return base * (1 - age / decay_days)
    except (ValueError, TypeError):
        return base


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
    path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def append_learning(learning: Learning, project_dir: Optional[str] = None) -> None:
    learning.timestamp = datetime.now(timezone.utc).isoformat()
    learning.project = project_dir or ""
    items = load_queue(project_dir)
    items.append(asdict(learning))
    if len(items) > MAX_QUEUE_SIZE:
        items.sort(key=effective_confidence)
        items = items[len(items) - MAX_QUEUE_SIZE :]
    save_queue(items, project_dir)


def prune_stale(project_dir: Optional[str] = None) -> int:
    """Remove items whose confidence has decayed to zero. Returns count removed."""
    items = load_queue(project_dir)
    before = len(items)
    items = [i for i in items if effective_confidence(i) > 0]
    if len(items) < before:
        save_queue(items, project_dir)
    return before - len(items)


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
