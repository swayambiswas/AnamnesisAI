"""
Memory classification module.
Determines memory type, confidence, temporal attributes, and intent
(e.g., explicit forget vs normal statement vs tentative goal).
"""

import re
from datetime import datetime
from typing import Optional, Tuple
from memory_engine.models import MemoryType


PREFERENCE_KEYWORDS = ["prefer", "love", "like", "favorite", "enjoy", "hate", "dislike"]
SKILL_KEYWORDS = ["use", "code in", "program in", "know", "learned", "developer", "proficient", "skill"]
LOCATION_KEYWORDS = ["live in", "moved to", "reside in", "from", "born in", "staying in"]
RELATIONSHIP_KEYWORDS = ["friend", "colleague", "manager", "boss", "wife", "husband", "partner", "sister", "brother"]
GOAL_KEYWORDS = ["want to", "plan to", "aim to", "might", "hoping to", "considering", "wish to"]
PROJECT_KEYWORDS = ["working on", "building", "assignment", "project", "implementing", "creating"]
EVENT_KEYWORDS = ["today", "tomorrow", "yesterday", "meeting", "conference", "party", "hackathon"]

FORGET_PATTERNS = [
    r"\bforget\b",
    r"\berase\b",
    r"\bdelete\s+(that|memory|info)\b",
    r"\bnever\s+mind\s+about\b",
    r"\bremove\s+record\b",
]

TENTATIVE_PATTERNS = [
    r"\bmight\b",
    r"\bmaybe\b",
    r"\bprobably\b",
    r"\bperhaps\b",
    r"\bthinking\s+of\b",
    r"\bnot\s+sure\b",
]


def is_explicit_forget_request(text: str) -> bool:
    """Detects whether user is explicitly instructing the assistant to forget information."""
    text_lower = text.lower()
    for pattern in FORGET_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def is_tentative_statement(text: str) -> bool:
    """Detects tentative/probabilistic statements vs firm explicit commitments."""
    text_lower = text.lower()
    for pattern in TENTATIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def classify_memory_type(predicate: str, object_text: str, context: str = "") -> MemoryType:
    """
    Classifies the MemoryType based on predicate, object, and original context.
    """
    combined = f"{predicate} {object_text} {context}".lower()

    if any(k in combined for k in PREFERENCE_KEYWORDS):
        return MemoryType.PREFERENCE
    if any(k in combined for k in LOCATION_KEYWORDS):
        return MemoryType.LOCATION
    if any(k in combined for k in RELATIONSHIP_KEYWORDS):
        return MemoryType.RELATIONSHIP
    if any(k in combined for k in GOAL_KEYWORDS):
        return MemoryType.GOAL
    if any(k in combined for k in PROJECT_KEYWORDS):
        return MemoryType.PROJECT
    if any(k in combined for k in SKILL_KEYWORDS):
        return MemoryType.SKILL
    if any(k in combined for k in EVENT_KEYWORDS):
        return MemoryType.EVENT

    return MemoryType.FACT


def calculate_initial_confidence(
    text: str,
    is_explicit: bool = True,
    is_weak_inference: bool = False,
) -> float:
    """
    Computes initial confidence heuristic:
    - Explicit direct statement: ~0.92
    - Tentative statement ("I might learn Rust"): ~0.55
    - Weak inference: ~0.50
    """
    if is_weak_inference:
        return 0.50

    if is_tentative_statement(text):
        return 0.55

    if is_explicit:
        return 0.92

    return 0.70

