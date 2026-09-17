"""
Unit tests for the Memory Engine.
Strictly verifies the 10 required test scenarios:
1. New memory
2. Duplicate memory
3. Contradictory memory
4. Temporal change
5. Temporary information
6. Explicit forgetting
7. Confidence changes
8. Multiple users
9. Historical retrieval
10. Unrelated information
"""

from datetime import datetime, timedelta
import pytest

from memory_engine.models import (
    Memory,
    MemoryCandidate,
    MemoryStatus,
    MemoryType,
    ConflictType,
    ResolutionAction,
)
from memory_engine.engine import MemoryEngine
from memory_engine.temporal import is_valid_at, order_timeline, filter_timeline_at
from memory_engine.decay import apply_decay, calculate_decayed_confidence


@pytest.fixture
def base_time():
    return datetime(2026, 9, 17, 12, 0, 0)


# ==========================================
# 1. NEW MEMORY
# ==========================================
def test_1_new_memory(base_time):
    user_id = "user_101"
    msg = "I love Python."

    plan = MemoryEngine.process_message(
        message=msg,
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )

    assert len(plan.memories_to_add) == 1
    assert len(plan.memories_to_update) == 0

    mem = plan.memories_to_add[0]
    assert mem.user_id == user_id
    assert mem.subject == "user"
    assert mem.predicate == "prefers"
    assert mem.object_ == "Python"
    assert mem.memory_type == MemoryType.PREFERENCE
    assert mem.status == MemoryStatus.ACTIVE
    assert mem.confidence >= 0.90
    assert mem.source_message_id == "msg_001"


# ==========================================
# 2. DUPLICATE MEMORY
# ==========================================
def test_2_duplicate_memory(base_time):
    user_id = "user_102"
    # Seed existing memory
    plan1 = MemoryEngine.process_message(
        message="I love Python.",
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )
    existing_mem = plan1.memories_to_add[0]
    initial_conf = existing_mem.confidence

    # Second message with identical fact 5 days later
    later_time = base_time + timedelta(days=5)
    plan2 = MemoryEngine.process_message(
        message="I love Python.",
        user_id=user_id,
        message_id="msg_002",
        existing_memories=[existing_mem],
        current_time=later_time,
    )

    # Should not create duplicate memory
    assert len(plan2.memories_to_add) == 0
    assert len(plan2.memories_to_update) == 1

    updated_mem = plan2.memories_to_update[0]
    assert updated_mem.id == existing_mem.id
    assert updated_mem.confidence > initial_conf
    assert updated_mem.source_message_id == "msg_002"
    assert updated_mem.updated_at == later_time


# ==========================================
# 3. CONTRADICTORY MEMORY
# ==========================================
def test_3_contradictory_memory(base_time):
    user_id = "user_103"
    # User originally prefers Java
    plan1 = MemoryEngine.process_message(
        message="I love Java.",
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )
    old_mem = plan1.memories_to_add[0]

    # Later: switches to C++
    switch_time = base_time + timedelta(days=30)
    plan2 = MemoryEngine.process_message(
        message="I've switched from Java to C++ for my projects.",
        user_id=user_id,
        message_id="msg_002",
        existing_memories=[old_mem],
        current_time=switch_time,
    )

    assert len(plan2.memories_to_add) == 1
    assert len(plan2.memories_to_update) == 1

    new_mem = plan2.memories_to_add[0]
    superseded_mem = plan2.memories_to_update[0]

    # Check new memory
    assert new_mem.object_ == "C++"
    assert new_mem.status == MemoryStatus.ACTIVE
    assert new_mem.supersedes == old_mem.id
    assert new_mem.valid_from == switch_time

    # Check old memory superseded with audit link and closed interval
    assert superseded_mem.id == old_mem.id
    assert superseded_mem.status == MemoryStatus.SUPERSEDED
    assert superseded_mem.superseded_by == new_mem.id
    assert superseded_mem.valid_until == switch_time


# ==========================================
# 4. TEMPORAL CHANGE
# ==========================================
def test_4_temporal_change(base_time):
    user_id = "user_104"

    # Kolkata from 2020 to 2025
    plan1 = MemoryEngine.process_message(
        message="I lived in Kolkata from 2020 to 2025.",
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )
    kolkata_mem = plan1.memories_to_add[0]
    assert kolkata_mem.valid_from == datetime(2020, 1, 1)
    assert kolkata_mem.valid_until == datetime(2025, 12, 31, 23, 59, 59)

    # Chennai now
    plan2 = MemoryEngine.process_message(
        message="I live in Chennai now.",
        user_id=user_id,
        message_id="msg_002",
        existing_memories=[kolkata_mem],
        current_time=base_time,
    )

    # Should NOT supersede Kolkata because their valid intervals are non-overlapping
    assert len(plan2.memories_to_add) == 1
    assert len(plan2.memories_to_update) == 0

    chennai_mem = plan2.memories_to_add[0]
    assert chennai_mem.object_ == "Chennai"
    assert chennai_mem.status == MemoryStatus.ACTIVE
    assert chennai_mem.valid_from == base_time
    assert chennai_mem.valid_until is None


# ==========================================
# 5. TEMPORARY INFORMATION
# ==========================================
def test_5_temporary_information(base_time):
    user_id = "user_105"

    plan = MemoryEngine.process_message(
        message="I'm working on my DBMS assignment today.",
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )

    temp_mem = plan.memories_to_add[0]
    assert temp_mem.memory_type == MemoryType.EVENT
    assert temp_mem.status == MemoryStatus.ACTIVE

    # Simulate 30 days later (EVENT has a 7-day half-life)
    later_time = base_time + timedelta(days=30)
    decayed_mem = MemoryEngine.calculate_decay(temp_mem, current_time=later_time)

    # Confidence should have fallen well below 0.25 archive threshold
    assert decayed_mem.confidence < 0.25
    assert decayed_mem.status == MemoryStatus.ARCHIVED


# ==========================================
# 6. EXPLICIT FORGETTING
# ==========================================
def test_6_explicit_forgetting(base_time):
    user_id = "user_106"

    # Store a memory
    plan1 = MemoryEngine.process_message(
        message="I love Python.",
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )
    python_mem = plan1.memories_to_add[0]

    # Explicit instruction to forget
    forget_time = base_time + timedelta(days=2)
    plan2 = MemoryEngine.process_message(
        message="Forget that I ever told you about Python.",
        user_id=user_id,
        message_id="msg_002",
        existing_memories=[python_mem],
        current_time=forget_time,
    )

    assert len(plan2.memories_to_add) == 0
    assert len(plan2.memories_to_update) == 1

    forgotten_mem = plan2.memories_to_update[0]
    assert forgotten_mem.id == python_mem.id
    assert forgotten_mem.status == MemoryStatus.FORGOTTEN
    assert forgotten_mem.object_ == "[REDACTED]"

    # Test retrieval ignores forgotten memory
    active_mems = MemoryEngine.retrieve_memory_state(
        memories=[forgotten_mem],
        user_id=user_id,
    )
    assert len(active_mems) == 0


# ==========================================
# 7. CONFIDENCE CHANGES
# ==========================================
def test_7_confidence_changes(base_time):
    user_id = "user_107"

    # Tentative statement
    plan = MemoryEngine.process_message(
        message="I might learn Rust next semester.",
        user_id=user_id,
        message_id="msg_001",
        existing_memories=[],
        current_time=base_time,
    )
    tentative_mem = plan.memories_to_add[0]
    # Tentative statements get lower initial confidence
    assert tentative_mem.confidence <= 0.60

    # Reinforce confidence
    boosted = MemoryEngine.calculate_confidence(tentative_mem, boost_rate=0.20)
    assert boosted > tentative_mem.confidence

    # Decay confidence over time
    decayed_val = calculate_decayed_confidence(
        initial_confidence=boosted,
        memory_type=MemoryType.GOAL.value,
        days_elapsed=120,
    )
    assert decayed_val < boosted


# ==========================================
# 8. MULTIPLE USERS
# ==========================================
def test_8_multiple_users(base_time):
    user_a = "user_alice"
    user_b = "user_bob"

    # Alice prefers Python
    plan_a = MemoryEngine.process_message(
        message="I love Python.",
        user_id=user_a,
        message_id="msg_a1",
        existing_memories=[],
        current_time=base_time,
    )
    mem_alice = plan_a.memories_to_add[0]

    # Bob prefers Java
    plan_b = MemoryEngine.process_message(
        message="I love Java.",
        user_id=user_b,
        message_id="msg_b1",
        existing_memories=[mem_alice],  # Even if database passed all rows
        current_time=base_time,
    )
    mem_bob = plan_b.memories_to_add[0]

    # No conflict should occur between Alice and Bob
    assert len(plan_b.memories_to_update) == 0
    assert mem_bob.user_id == user_b

    # Verify query isolation
    all_stored = [mem_alice, mem_bob]
    alice_mems = MemoryEngine.retrieve_memory_state(all_stored, user_id=user_a)
    bob_mems = MemoryEngine.retrieve_memory_state(all_stored, user_id=user_b)

    assert len(alice_mems) == 1
    assert alice_mems[0].object_ == "Python"

    assert len(bob_mems) == 1
    assert bob_mems[0].object_ == "Java"


# ==========================================
# 9. HISTORICAL RETRIEVAL
# ==========================================
def test_9_historical_retrieval(base_time):
    user_id = "user_109"

    mem_kolkata = Memory(
        id="mem_kol",
        user_id=user_id,
        subject="user",
        predicate="lives_in",
        object="Kolkata",
        memory_type=MemoryType.LOCATION,
        confidence=0.95,
        status=MemoryStatus.ACTIVE,
        valid_from=datetime(2020, 1, 1),
        valid_until=datetime(2025, 1, 1),
        created_at=datetime(2025, 1, 1),
        updated_at=datetime(2025, 1, 1),
        source_message_id="msg_01",
    )

    mem_chennai = Memory(
        id="mem_che",
        user_id=user_id,
        subject="user",
        predicate="lives_in",
        object="Chennai",
        memory_type=MemoryType.LOCATION,
        confidence=0.95,
        status=MemoryStatus.ACTIVE,
        valid_from=datetime(2025, 1, 2),
        valid_until=None,
        created_at=datetime(2025, 1, 2),
        updated_at=datetime(2025, 1, 2),
        source_message_id="msg_02",
    )

    all_mems = [mem_kolkata, mem_chennai]

    # Point in time query: 2022 -> where did I live?
    res_2022 = MemoryEngine.retrieve_memory_state(
        all_mems,
        user_id=user_id,
        target_time=datetime(2022, 6, 1),
        predicate="lives_in",
    )
    assert len(res_2022) == 1
    assert res_2022[0].object_ == "Kolkata"

    # Current query (2026) -> where do I live now?
    res_now = MemoryEngine.retrieve_memory_state(
        all_mems,
        user_id=user_id,
        predicate="lives_in",
    )
    # Default without target_time returns active memories
    assert any(m.object_ == "Chennai" for m in res_now)

    # Chronological timeline
    ordered = order_timeline(all_mems, predicate="lives_in")
    assert ordered[0].object_ == "Kolkata"
    assert ordered[1].object_ == "Chennai"


# ==========================================
# 10. UNRELATED INFORMATION
# ==========================================
def test_10_unrelated_information(base_time):
    user_id = "user_110"

    existing_name = Memory(
        id="mem_name",
        user_id=user_id,
        subject="user",
        predicate="name",
        object="Aditya",
        memory_type=MemoryType.FACT,
        confidence=0.99,
        status=MemoryStatus.ACTIVE,
        valid_from=base_time,
        valid_until=None,
        created_at=base_time,
        updated_at=base_time,
        source_message_id="msg_01",
    )

    # Completely unrelated new statement: "I love Python"
    plan = MemoryEngine.process_message(
        message="I love Python.",
        user_id=user_id,
        message_id="msg_02",
        existing_memories=[existing_name],
        current_time=base_time,
    )

    # Should not trigger false contradiction or overwrite name
    assert len(plan.memories_to_add) == 1
    assert len(plan.memories_to_update) == 0
    assert plan.memories_to_add[0].predicate == "prefers"
    assert plan.memories_to_add[0].object_ == "Python"

