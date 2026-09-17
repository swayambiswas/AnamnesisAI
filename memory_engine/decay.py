"""
Memory decay and confidence adjustment module.
Applies half-life based decay to memories according to their MemoryType,
and handles transitions: active -> stale/archived or expired.
"""

from datetime import datetime
from typing import Dict
from memory_engine.models import Memory, MemoryType, MemoryStatus

# Half-life in days for each memory type
HALF_LIVES_DAYS: Dict[str, float] = {
    MemoryType.FACT.value: 365.0,         # Permanent-ish
    MemoryType.RELATIONSHIP.value: 365.0, # Permanent-ish
    MemoryType.LOCATION.value: 180.0,     # Slow
    MemoryType.SKILL.value: 120.0,        # Medium
    MemoryType.PREFERENCE.value: 90.0,    # Medium
    MemoryType.GOAL.value: 60.0,          # Medium-fast
    MemoryType.PROJECT.value: 30.0,       # Fast
    MemoryType.EVENT.value: 7.0,          # Very fast
}

ARCHIVE_THRESHOLD = 0.25
EXPIRED_THRESHOLD = 0.10


def calculate_decayed_confidence(
    initial_confidence: float,
    memory_type: str,
    days_elapsed: float,
) -> float:
    """
    Calculates decayed confidence using exponential decay based on half-life.
    c(t) = c_0 * (0.5 ** (t / half_life))
    """
    half_life = HALF_LIVES_DAYS.get(memory_type, 90.0)
    if days_elapsed <= 0:
        return initial_confidence

    decay_factor = 0.5 ** (days_elapsed / half_life)
    new_confidence = initial_confidence * decay_factor
    return round(max(0.0, min(1.0, new_confidence)), 4)


def reinforce_confidence(current_confidence: float, boost_rate: float = 0.15) -> float:
    """
    Reinforces confidence upon repeated observation.
    diminishing returns: 1 - (1 - c) * (1 - boost)
    """
    new_conf = 1.0 - (1.0 - current_confidence) * (1.0 - boost_rate)
    return round(min(0.99, max(0.0, new_conf)), 4)


def apply_decay(memory: Memory, current_time: datetime) -> Memory:
    """
    Evaluates a memory at current_time and returns an updated copy if decayed or expired.
    Preserves audit history; does not mutate immutable fields.
    """
    # Don't decay memories that are already superseded or forgotten
    if memory.status in [MemoryStatus.FORGOTTEN, MemoryStatus.SUPERSEDED]:
        return memory

    # Check explicit expiration date
    if memory.valid_until and current_time > memory.valid_until:
        updated = memory.copy(deep=True)
        updated.status = MemoryStatus.EXPIRED
        updated.updated_at = current_time
        return updated

    # Calculate days since last update
    days_elapsed = (current_time - memory.updated_at).total_seconds() / 86400.0
    if days_elapsed <= 0:
        return memory

    mem_type = memory.memory_type.value if hasattr(memory.memory_type, "value") else str(memory.memory_type)
    decayed_conf = calculate_decayed_confidence(memory.confidence, mem_type, days_elapsed)

    updated = memory.copy(deep=True)
    updated.confidence = decayed_conf

    # Check if confidence dropped low enough to archive
    if memory.status == MemoryStatus.ACTIVE and decayed_conf < ARCHIVE_THRESHOLD:
        updated.status = MemoryStatus.ARCHIVED
        updated.updated_at = current_time

    return updated

