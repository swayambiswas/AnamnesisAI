"""
Conflict detection module.
Evaluates candidates against existing active memories to detect:
- Duplicates (reinforce confidence)
- Contradictions (supersede old with new)
- Temporal updates (distinct non-overlapping timelines)
- Explicit forgets
"""

from typing import List, Optional
from memory_engine.models import (
    Memory,
    MemoryCandidate,
    ConflictResult,
    ConflictType,
    ResolutionAction,
)
from memory_engine.temporal import intervals_overlap


def _normalize(val: str) -> str:
    return val.strip().lower()


def detect_candidate_conflict(
    candidate: MemoryCandidate,
    existing_memory: Memory,
) -> Optional[ConflictResult]:
    """
    Evaluates a candidate against a single active memory for conflict or equivalence.
    Strictly checks that user_ids match.
    """
    # Strict multi-user isolation
    if candidate.user_id != existing_memory.user_id:
        return None

    # Handle Explicit Forget
    if candidate.is_explicit_forget:
        # Check if candidate topic/object matches existing predicate, object, or context
        target = _normalize(candidate.object_)
        if (
            target in _normalize(existing_memory.object_)
            or target in _normalize(existing_memory.predicate)
            or _normalize(existing_memory.object_) in target
        ):
            return ConflictResult(
                conflict=True,
                conflict_type=ConflictType.EXPLICIT_FORGET,
                candidate=candidate,
                existing_memory_id=existing_memory.id,
                existing_memory=existing_memory,
                resolution=ResolutionAction.FORGET,
                explanation=f"User explicitly requested to forget memory '{existing_memory.predicate}: {existing_memory.object_}'",
            )
        return None

    same_subject = _normalize(candidate.subject) == _normalize(existing_memory.subject)
    same_predicate = _normalize(candidate.predicate) == _normalize(existing_memory.predicate)
    same_object = _normalize(candidate.object_) == _normalize(existing_memory.object_)

    if not same_subject or not same_predicate:
        return None

    # 1. Exact Duplicate
    if same_object:
        return ConflictResult(
            conflict=False,
            conflict_type=ConflictType.DUPLICATE,
            candidate=candidate,
            existing_memory_id=existing_memory.id,
            existing_memory=existing_memory,
            resolution=ResolutionAction.REINFORCE_DUPLICATE,
            explanation=f"Exact duplicate observed for '{candidate.subject} {candidate.predicate} {candidate.object_}'. Reinforcing confidence.",
        )

    # 2. Same subject & predicate, but different object -> Potential contradiction or temporal shift
    overlaps = intervals_overlap(
        candidate.valid_from,
        candidate.valid_until,
        existing_memory.valid_from,
        existing_memory.valid_until,
    )

    if not overlaps:
        # Validity intervals are disjoint! (e.g., 2020-2025 vs 2025-present)
        return ConflictResult(
            conflict=False,
            conflict_type=ConflictType.TEMPORAL_UPDATE,
            candidate=candidate,
            existing_memory_id=existing_memory.id,
            existing_memory=existing_memory,
            resolution=ResolutionAction.KEEP_BOTH_TEMPORAL,
            explanation=(
                f"Temporal shift detected for {candidate.predicate}. "
                f"Old: '{existing_memory.object_}', New: '{candidate.object_}' with non-overlapping valid periods."
            ),
        )
    else:
        # Validity intervals overlap -> Contradiction! (Must supersede old with new)
        return ConflictResult(
            conflict=True,
            conflict_type=ConflictType.CONTRADICTION,
            candidate=candidate,
            existing_memory_id=existing_memory.id,
            existing_memory=existing_memory,
            resolution=ResolutionAction.SUPERSEDE,
            explanation=(
                f"Contradiction detected: '{existing_memory.object_}' conflicts with newer '{candidate.object_}' "
                f"for {candidate.predicate}. Old memory will be superseded."
            ),
        )


def detect_conflicts(
    candidate: MemoryCandidate,
    existing_memories: List[Memory],
) -> List[ConflictResult]:
    """
    Scans a list of active memories for conflicts with the candidate.
    """
    results: List[ConflictResult] = []
    for mem in existing_memories:
        if mem.status == "forgotten":
            continue
        c_res = detect_candidate_conflict(candidate, mem)
        if c_res:
            results.append(c_res)

    if not results and not candidate.is_explicit_forget:
        results.append(
            ConflictResult(
                conflict=False,
                conflict_type=ConflictType.NONE,
                candidate=candidate,
                existing_memory_id=None,
                existing_memory=None,
                resolution=ResolutionAction.ADD_NEW,
                explanation="No conflict detected. Clean new memory.",
            )
        )

    return results

