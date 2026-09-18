"""Tests for the ContextBuilder formatting."""
from datetime import datetime
import pytest

from agent.context import ContextBuilder
from agent.models import MemoryRecord, MemoryStatus, RetrievalResult


@pytest.fixture
def builder():
    return ContextBuilder()


def test_context_builder(builder):
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
    instruction = "Answer the user."
    user_query = "Do I like apples?"

    context_str = builder.build_context([res1], instruction, user_query)

    assert "=== SYSTEM INSTRUCTIONS ===" in context_str
    assert "Answer the user." in context_str
    assert "=== USER QUERY ===" in context_str
    assert "Do I like apples?" in context_str
    assert "=== MEMORY DATA (UNTRUSTED" in context_str
    assert "I like apples" in context_str
    assert "[ID: mem1]" in context_str
    assert "Subject: I" in context_str
    assert "Predicate: like" in context_str
    assert "Object: apples" in context_str
    assert "Confidence: 1.0" in context_str


def test_empty_retrieval(builder):
    instruction = "Answer the user."
    context_str = builder.build_context([], instruction)

    assert "=== SYSTEM INSTRUCTIONS ===" in context_str
    assert "Answer the user." in context_str
    assert "No relevant memories found." in context_str
    assert "=== USER QUERY ===" not in context_str
