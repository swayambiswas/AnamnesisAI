"""Tests for ProvenanceManager deduplication and generation."""
from datetime import datetime

from agent.models import MemoryRecord, MemoryStatus, RetrievalResult
from agent.provenance import ProvenanceManager


def test_provenance_generation():
    ref_time = datetime(2026, 9, 18)
    mem1 = MemoryRecord(
        id="mem1",
        user_id="user1",
        subject="I",
        predicate="like",
        object="apples",
        memory_type="preference",
        content="I like apples",
        confidence=1.0,
        status=MemoryStatus.ACTIVE,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
    )
    mem2 = mem1.model_copy(
        update={"id": "mem2", "status": MemoryStatus.SUPERSEDED}
    )

    res1 = RetrievalResult(memory=mem1, score=1.0)
    res2 = RetrievalResult(memory=mem2, score=0.9)

    provenance = ProvenanceManager.generate_provenance(
        [res1, res2], ref_time
    )

    assert len(provenance) == 2
    assert provenance[0].memory_id == "mem1"
    assert "active_memory" in provenance[0].reason
    assert "current_state_match" in provenance[0].reason

    assert provenance[1].memory_id == "mem2"
    assert provenance[1].status == "superseded"
    assert "active_memory" not in provenance[1].reason
    assert "current_state_match" not in provenance[1].reason


def test_provenance_deduplication():
    ref_time = datetime(2026, 9, 18)
    mem1 = MemoryRecord(
        id="mem1",
        user_id="user1",
        subject="I",
        predicate="like",
        object="apples",
        memory_type="preference",
        content="I like apples",
        confidence=1.0,
        status=MemoryStatus.ACTIVE,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
    )

    res1 = RetrievalResult(memory=mem1, score=1.0)
    res2 = RetrievalResult(memory=mem1, score=0.9)

    provenance = ProvenanceManager.generate_provenance(
        [res1, res2], ref_time
    )

    assert len(provenance) == 1
    assert provenance[0].memory_id == "mem1"


def test_provenance_empty():
    res = ProvenanceManager.generate_provenance([], datetime(2026, 9, 18))
    assert res == []
