"""Tests for Pydantic data models."""
from datetime import datetime

import pytest
from pydantic import ValidationError

from agent.models import (
    MemoryRecord,
    MemoryStatus,
)


# ── helpers ──────────────────────────────────────────────────────

def _make_memory(**overrides):
    defaults = dict(
        id="mem1",
        user_id="user1",
        subject="I",
        predicate="like",
        object="apples",
        memory_type="preference",
        content="I like apples",
        confidence=0.9,
        status=MemoryStatus.ACTIVE,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
    )
    defaults.update(overrides)
    return MemoryRecord(**defaults)


# ── model construction ───────────────────────────────────────────

class TestMemoryRecordValidation:
    def test_valid_construction(self):
        mem = _make_memory()
        assert mem.id == "mem1"
        assert mem.status == MemoryStatus.ACTIVE

    def test_missing_required_fields_rejected(self):
        with pytest.raises(ValidationError):
            MemoryRecord(id="x", user_id="u")  # type: ignore[call-arg]

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            _make_memory(status="invalid_status")

    def test_optional_fields_default_to_none(self):
        mem = _make_memory()
        assert mem.valid_from is None
        assert mem.valid_until is None
        assert mem.source_message_id is None
        assert mem.supersedes is None


# ── confidence bounds ────────────────────────────────────────────

class TestConfidenceBounds:
    def test_confidence_above_1_rejected(self):
        with pytest.raises(ValidationError):
            _make_memory(confidence=1.5)

    def test_confidence_below_0_rejected(self):
        with pytest.raises(ValidationError):
            _make_memory(confidence=-0.1)

    def test_confidence_at_boundaries_accepted(self):
        assert _make_memory(confidence=0.0).confidence == 0.0
        assert _make_memory(confidence=1.0).confidence == 1.0


# ── temporal consistency ─────────────────────────────────────────

class TestTemporalConsistency:
    def test_valid_from_before_valid_until_accepted(self):
        mem = _make_memory(
            valid_from=datetime(2023, 1, 1),
            valid_until=datetime(2024, 1, 1),
        )
        assert mem.valid_from < mem.valid_until

    def test_valid_from_equals_valid_until_rejected(self):
        with pytest.raises(ValidationError, match="strictly before"):
            _make_memory(
                valid_from=datetime(2023, 1, 1),
                valid_until=datetime(2023, 1, 1),
            )

    def test_valid_from_after_valid_until_rejected(self):
        with pytest.raises(ValidationError, match="strictly before"):
            _make_memory(
                valid_from=datetime(2024, 1, 1),
                valid_until=datetime(2023, 1, 1),
            )

    def test_only_valid_from_accepted(self):
        mem = _make_memory(valid_from=datetime(2023, 6, 1))
        assert mem.valid_until is None

    def test_only_valid_until_accepted(self):
        mem = _make_memory(valid_until=datetime(2024, 1, 1))
        assert mem.valid_from is None


# ── user isolation ───────────────────────────────────────────────

class TestUserIsolation:
    def test_user_id_is_required(self):
        with pytest.raises(ValidationError):
            MemoryRecord(
                id="mem1",
                subject="I",
                predicate="like",
                object="apples",
                memory_type="preference",
                content="I like apples",
                confidence=0.9,
                status=MemoryStatus.ACTIVE,
                created_at=datetime(2023, 1, 1),
                updated_at=datetime(2023, 1, 1),
            )  # type: ignore[call-arg]
