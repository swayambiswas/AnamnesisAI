"""
Memory extraction module.
Identifies information worth remembering from user messages, distinguishing
explicit statements, transitions, temporal qualifications, and forget commands.
Supports both deterministic rule-based parsing and pluggable LLM extraction.
"""

import re
import json
from datetime import datetime
from typing import List, Optional, Callable, Dict, Any, Tuple
from memory_engine.models import MemoryCandidate, MemoryType
from memory_engine.classifier import (
    is_explicit_forget_request,
    classify_memory_type,
    calculate_initial_confidence,
)


def _extract_year_range(text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
    # Matches patterns like "from 2020 to 2025" or "between 2020 and 2025" or "in 2022"
    m_range = re.search(r"\bfrom\s+(\d{4})\s+to\s+(\d{4})\b", text, re.IGNORECASE)
    if m_range:
        y1, y2 = int(m_range.group(1)), int(m_range.group(2))
        return datetime(y1, 1, 1), datetime(y2, 12, 31, 23, 59, 59)

    m_between = re.search(r"\bbetween\s+(\d{4})\s+and\s+(\d{4})\b", text, re.IGNORECASE)
    if m_between:
        y1, y2 = int(m_between.group(1)), int(m_between.group(2))
        return datetime(y1, 1, 1), datetime(y2, 12, 31, 23, 59, 59)

    m_single = re.search(r"\b(?:in|since)\s+(\d{4})\b", text, re.IGNORECASE)
    if m_single:
        y = int(m_single.group(1))
        return datetime(y, 1, 1), None

    return None, None


def _deterministic_extract(
    message: str,
    user_id: str,
    source_message_id: str,
    current_time: datetime,
) -> List[MemoryCandidate]:
    """
    Deterministic rule-based extractor for common memory patterns.
    """
    candidates: List[MemoryCandidate] = []
    text = message.strip()

    # 1. Check for explicit forget command
    if is_explicit_forget_request(text):
        # e.g., "Forget that I ever told you about Java" or "Forget my favorite language"
        forget_target = re.sub(r"^(please\s+)?(forget\s+that\s+i\s+ever\s+told\s+you\s+(about\s+)?|forget\s+(about\s+)?|erase\s+(memory\s+about\s+)?)", "", text, flags=re.IGNORECASE).strip()
        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate="forgotten_topic",
                object=forget_target or text,
                memory_type=MemoryType.FACT,
                confidence=1.0,
                source_message_id=source_message_id,
                is_explicit_forget=True,
                raw_text=text,
            )
        )
        return candidates

    # 2. Check for transition: "I've switched from X to Y for Z"
    switch_match = re.search(
        r"(?:i've|i\s+have|i)\s+switched\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+for\s+(.+))?$",
        text,
        re.IGNORECASE,
    )
    if switch_match:
        old_val = switch_match.group(1).strip()
        new_val = switch_match.group(2).strip()
        context = switch_match.group(3) or "general"
        predicate = "prefers" if "for" in text else "uses"

        # The new memory
        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate=predicate,
                object=new_val,
                memory_type=MemoryType.PREFERENCE if predicate == "prefers" else MemoryType.SKILL,
                confidence=0.95,
                valid_from=current_time,
                valid_until=None,
                source_message_id=source_message_id,
                raw_text=text,
            )
        )
        return candidates

    # 3. Temporal residence: "I lived in Kolkata from 2020 to 2025" or "I live in Chennai now"
    lived_match = re.search(r"i\s+(?:lived|live)\s+in\s+([A-Za-z\s]+?)(?:\s+(?:from|between|in|now|since).*)?$", text, re.IGNORECASE)
    if lived_match:
        city = lived_match.group(1).strip()
        # strip trailing prepositions
        city = re.sub(r"\s+(from|between|in|now|since)$", "", city, flags=re.IGNORECASE).strip()
        start_d, end_d = _extract_year_range(text)
        if "now" in text.lower() or "currently" in text.lower():
            start_d = current_time
            end_d = None
        elif not start_d and "lived" in text.lower():
            end_d = current_time

        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate="lives_in",
                object=city,
                memory_type=MemoryType.LOCATION,
                confidence=0.95,
                valid_from=start_d,
                valid_until=end_d,
                source_message_id=source_message_id,
                raw_text=text,
            )
        )
        return candidates

    # 4. Preferences: "I love Python", "I prefer X", "I like Y"
    pref_match = re.search(
        r"i\s+(love|like|prefer|enjoy|hate|dislike)\s+(.+?)(?:\s*\.|\s*!|$)",
        text,
        re.IGNORECASE,
    )
    if pref_match:
        verb = pref_match.group(1).lower()
        obj = pref_match.group(2).strip()
        predicate = "prefers" if verb in ["love", "like", "prefer", "enjoy"] else "dislikes"
        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate=predicate,
                object=obj,
                memory_type=MemoryType.PREFERENCE,
                confidence=calculate_initial_confidence(text, is_explicit=True),
                valid_from=current_time,
                source_message_id=source_message_id,
                raw_text=text,
            )
        )
        return candidates

    # 5. Tentative goals: "I might learn Rust next semester" / "I want to learn Go"
    goal_match = re.search(
        r"i\s+(might\s+learn|want\s+to\s+learn|plan\s+to\s+learn|aim\s+to\s+learn)\s+(.+?)(?:\s*\.|\s*!|$)",
        text,
        re.IGNORECASE,
    )
    if goal_match:
        obj = goal_match.group(2).strip()
        is_tentative = "might" in goal_match.group(1).lower()
        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate="goal_to_learn",
                object=obj,
                memory_type=MemoryType.GOAL,
                confidence=0.55 if is_tentative else 0.85,
                valid_from=current_time,
                source_message_id=source_message_id,
                raw_text=text,
            )
        )
        return candidates

    # 6. Projects / Tasks: "I'm working on my DBMS assignment today"
    project_match = re.search(
        r"(?:i'm|i\s+am)\s+working\s+on\s+(.+?)(?:\s*\.|\s*!|$)",
        text,
        re.IGNORECASE,
    )
    if project_match:
        obj = project_match.group(1).strip()
        # check if it mentions today/temporary
        is_today = "today" in text.lower() or "tonight" in text.lower()
        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate="working_on",
                object=obj,
                memory_type=MemoryType.EVENT if is_today else MemoryType.PROJECT,
                confidence=0.90,
                valid_from=current_time,
                source_message_id=source_message_id,
                raw_text=text,
            )
        )
        return candidates

    # 7. Basic Identity / Facts: "My name is Aditya"
    name_match = re.search(r"my\s+name\s+is\s+([A-Za-z\s]+?)(?:\s*\.|$)", text, re.IGNORECASE)
    if name_match:
        name = name_match.group(1).strip()
        candidates.append(
            MemoryCandidate(
                user_id=user_id,
                subject="user",
                predicate="name",
                object=name,
                memory_type=MemoryType.FACT,
                confidence=0.99,
                valid_from=current_time,
                source_message_id=source_message_id,
                raw_text=text,
            )
        )
        return candidates

    return candidates


def extract_memories(
    message: str,
    user_id: str,
    source_message_id: str,
    current_time: Optional[datetime] = None,
    llm_callable: Optional[Callable[[str], str]] = None,
) -> List[MemoryCandidate]:
    """
    Main extraction interface.
    Extracts memory candidates from a user message.
    If an LLM callable is supplied by the AI Engineer, uses it with fallback
    to deterministic extraction.
    """
    now = current_time or datetime.utcnow()

    if llm_callable:
        try:
            # Prompt LLM for structured JSON
            prompt = (
                f"Extract structured memories from: '{message}'.\n"
                f"Respond with JSON list: [{{subject, predicate, object, memory_type, confidence, is_explicit_forget}}]"
            )
            raw_response = llm_callable(prompt)
            data = json.loads(raw_response)
            results = []
            for item in data:
                mtype = item.get("memory_type", "fact")
                results.append(
                    MemoryCandidate(
                        user_id=user_id,
                        subject=item.get("subject", "user"),
                        predicate=item.get("predicate", "statement"),
                        object=item.get("object", ""),
                        memory_type=MemoryType(mtype) if mtype in MemoryType.__members__.values() else MemoryType.FACT,
                        confidence=float(item.get("confidence", 0.8)),
                        source_message_id=source_message_id,
                        is_explicit_forget=bool(item.get("is_explicit_forget", False)),
                        valid_from=now,
                        raw_text=message,
                    )
                )
            if results:
                return results
        except Exception:
            # Graceful fallback to deterministic parser
            pass

    return _deterministic_extract(message, user_id, source_message_id, now)
