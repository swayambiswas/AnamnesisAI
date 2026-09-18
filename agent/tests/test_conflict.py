"""Tests for ConflictDetector."""
from datetime import datetime
from agent.models import MemoryRecord, MemoryStatus, RetrievalResult
from agent.conflict import ConflictDetector


def test_no_conflicts_with_distinct_predicates():
    ref = datetime(2026, 1, 1)
    mem1 = MemoryRecord(
        id="1", user_id="u", subject="User", predicate="uses", object="Python",
        memory_type="pref", content="a", confidence=1.0,
        status=MemoryStatus.ACTIVE, created_at=ref, updated_at=ref
    )
    mem2 = mem1.model_copy(
        update={"id": "2", "predicate": "likes", "object": "Java"}
    )

    assert not ConflictDetector.detect_conflicts([
        RetrievalResult(memory=mem1, score=1.0),
        RetrievalResult(memory=mem2, score=1.0)
    ], ref)


def test_conflict_detected_same_predicate_different_object():
    ref = datetime(2026, 1, 1)
    mem1 = MemoryRecord(
        id="1", user_id="u", subject="User", predicate="uses", object="Python",
        memory_type="pref", content="a", confidence=1.0,
        status=MemoryStatus.ACTIVE, created_at=ref, updated_at=ref
    )
    mem2 = mem1.model_copy(update={"id": "2", "object": "Java"})

    assert ConflictDetector.detect_conflicts([
        RetrievalResult(memory=mem1, score=1.0),
        RetrievalResult(memory=mem2, score=1.0)
    ], ref)


def test_no_conflict_if_one_is_superseded():
    ref = datetime(2026, 1, 1)
    mem1 = MemoryRecord(
        id="1", user_id="u", subject="User", predicate="uses", object="Python",
        memory_type="pref", content="a", confidence=1.0,
        status=MemoryStatus.SUPERSEDED, created_at=ref, updated_at=ref
    )
    mem2 = mem1.model_copy(
        update={"id": "2", "object": "Java", "status": MemoryStatus.ACTIVE}
    )

    assert not ConflictDetector.detect_conflicts([
        RetrievalResult(memory=mem1, score=1.0),
        RetrievalResult(memory=mem2, score=1.0)
    ], ref)
