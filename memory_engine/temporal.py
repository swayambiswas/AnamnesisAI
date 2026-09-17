"""
Temporal reasoning module for handling validity intervals, timeline queries,
and temporal conflict analysis.
"""

from datetime import datetime
from typing import Optional, List
from memory_engine.models import Memory


def intervals_overlap(
    start1: Optional[datetime],
    end1: Optional[datetime],
    start2: Optional[datetime],
    end2: Optional[datetime],
) -> bool:
    """
    Checks if two validity intervals [start1, end1] and [start2, end2] overlap.
    None for start is treated as -infinity.
    None for end is treated as +infinity (ongoing / present).
    """
    effective_start1 = start1 or datetime.min
    effective_end1 = end1 or datetime.max

    effective_start2 = start2 or datetime.min
    effective_end2 = end2 or datetime.max

    # Overlap occurs if the start of one is before the end of the other, mutually
    return max(effective_start1, effective_start2) < min(effective_end1, effective_end2)


def is_valid_at(memory: Memory, target_time: datetime) -> bool:
    """
    Evaluates whether a memory was valid at a specific point in time.
    """
    if memory.status == "forgotten":
        return False

    if memory.valid_from and target_time < memory.valid_from:
        return False

    if memory.valid_until and target_time > memory.valid_until:
        return False

    return True


def filter_timeline_at(
    memories: List[Memory],
    target_time: datetime,
    subject: Optional[str] = None,
    predicate: Optional[str] = None,
) -> List[Memory]:
    """
    Filters memories valid at a specific target_time, optionally by subject and predicate.
    """
    results = []
    for mem in memories:
        if mem.status == "forgotten":
            continue
        if subject and mem.subject.lower() != subject.lower():
            continue
        if predicate and mem.predicate.lower() != predicate.lower():
            continue
        if is_valid_at(mem, target_time):
            results.append(mem)
    return results


def order_timeline(
    memories: List[Memory],
    subject: Optional[str] = None,
    predicate: Optional[str] = None,
) -> List[Memory]:
    """
    Orders memories chronologically for timeline display and provenance explanations.
    """
    filtered = [
        mem
        for mem in memories
        if mem.status != "forgotten"
        and (not subject or mem.subject.lower() == subject.lower())
        and (not predicate or mem.predicate.lower() == predicate.lower())
    ]

    def sort_key(m: Memory):
        # Earliest valid_from, fallback to created_at
        return m.valid_from or m.created_at

    return sorted(filtered, key=sort_key)

