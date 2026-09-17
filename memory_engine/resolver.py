"""
Resolution module for executing deterministic memory state transitions:
- Adds new memories
- Supersedes old memories with audit links and closed validity intervals
- Reinforces duplicate memories
- Preserves distinct temporal memories
- Tombstones forgotten memories
"""

import uuid
from datetime import datetime
from typing import List, Optional
from memory_engine.models import (
    Memory,
    MemoryCandidate,
    MemoryStatus,
    ConflictResult,
    ResolutionAction,
    ResolutionPlan,
)
from memory_engine.decay import reinforce_confidence


def _generate_memory_id() -> str:
    return f"mem_{uuid.uuid4().hex[:8]}"


def resolve_conflict(
    conflict: ConflictResult,
    current_time: Optional[datetime] = None,
) -> ResolutionPlan:
    """
    Executes deterministic state transitions for a single conflict result.
    """
    now = current_time or datetime.utcnow()
    action = conflict.resolution
    cand = conflict.candidate
    existing = conflict.existing_memory

    # 1. ADD NEW
    if action == ResolutionAction.ADD_NEW:
        new_mem = Memory(
            id=_generate_memory_id(),
            user_id=cand.user_id,
            subject=cand.subject,
            predicate=cand.predicate,
            object=cand.object_,
            memory_type=cand.memory_type,
            confidence=cand.confidence,
            status=MemoryStatus.ACTIVE,
            valid_from=cand.valid_from or now,
            valid_until=cand.valid_until,
            created_at=now,
            updated_at=now,
            source_message_id=cand.source_message_id,
            supersedes=None,
            superseded_by=None,
            provenance_note=f"Created from message {cand.source_message_id}",
        )
        return ResolutionPlan(
            memories_to_add=[new_mem],
            memories_to_update=[],
            explanation=conflict.explanation,
        )

    # 2. REINFORCE DUPLICATE
    if action == ResolutionAction.REINFORCE_DUPLICATE and existing:
        updated = existing.copy(deep=True)
        updated.confidence = reinforce_confidence(existing.confidence)
        updated.updated_at = now
        updated.source_message_id = cand.source_message_id
        updated.provenance_note = f"Reinforced by message {cand.source_message_id}"
        return ResolutionPlan(
            memories_to_add=[],
            memories_to_update=[updated],
            explanation=conflict.explanation,
        )

    # 3. SUPERSEDE
    if action == ResolutionAction.SUPERSEDE and existing:
        new_id = _generate_memory_id()

        # Update existing memory to superseded
        old_updated = existing.copy(deep=True)
        old_updated.status = MemoryStatus.SUPERSEDED
        old_updated.superseded_by = new_id
        old_updated.valid_until = now
        old_updated.updated_at = now

        # Create new active memory
        new_mem = Memory(
            id=new_id,
            user_id=cand.user_id,
            subject=cand.subject,
            predicate=cand.predicate,
            object=cand.object_,
            memory_type=cand.memory_type,
            confidence=cand.confidence,
            status=MemoryStatus.ACTIVE,
            valid_from=cand.valid_from or now,
            valid_until=cand.valid_until,
            created_at=now,
            updated_at=now,
            source_message_id=cand.source_message_id,
            supersedes=existing.id,
            superseded_by=None,
            provenance_note=f"Superseded memory {existing.id} via message {cand.source_message_id}",
        )
        return ResolutionPlan(
            memories_to_add=[new_mem],
            memories_to_update=[old_updated],
            explanation=conflict.explanation,
        )

    # 4. KEEP BOTH TEMPORAL
    if action == ResolutionAction.KEEP_BOTH_TEMPORAL:
        new_mem = Memory(
            id=_generate_memory_id(),
            user_id=cand.user_id,
            subject=cand.subject,
            predicate=cand.predicate,
            object=cand.object_,
            memory_type=cand.memory_type,
            confidence=cand.confidence,
            status=MemoryStatus.ACTIVE,
            valid_from=cand.valid_from or now,
            valid_until=cand.valid_until,
            created_at=now,
            updated_at=now,
            source_message_id=cand.source_message_id,
            supersedes=None,
            superseded_by=None,
            provenance_note=f"Temporal fact recorded from message {cand.source_message_id}",
        )
        return ResolutionPlan(
            memories_to_add=[new_mem],
            memories_to_update=[],
            explanation=conflict.explanation,
        )

    # 5. FORGET
    if action == ResolutionAction.FORGET and existing:
        forgotten = existing.copy(deep=True)
        forgotten.status = MemoryStatus.FORGOTTEN
        forgotten.object_ = "[REDACTED]"
        forgotten.updated_at = now
        forgotten.provenance_note = f"Explicitly forgotten via message {cand.source_message_id}"
        return ResolutionPlan(
            memories_to_add=[],
            memories_to_update=[forgotten],
            explanation=conflict.explanation,
        )

    return ResolutionPlan(memories_to_add=[], memories_to_update=[], explanation="No action taken.")

