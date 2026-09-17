"""
MemoryEngine - High-level facade providing clean, deterministic interfaces
for Backend and Agent engineers.
"""

from datetime import datetime
from typing import List, Optional, Callable, Tuple
from memory_engine.models import (
    Memory,
    MemoryCandidate,
    ConflictResult,
    ResolutionPlan,
    MemoryStatus,
)
from memory_engine.extractor import extract_memories
from memory_engine.conflict import detect_conflicts
from memory_engine.resolver import resolve_conflict
from memory_engine.decay import apply_decay, reinforce_confidence
from memory_engine.temporal import filter_timeline_at, order_timeline, is_valid_at


class MemoryEngine:
    """
    Main memory engine orchestrator.
    Exposes all core capabilities requested by the project architecture:
    - Extraction & classification
    - Conflict & contradiction detection
    - Deterministic state transitions & versioning
    - Temporal reasoning & timeline filtering
    - Memory decay & confidence updates
    - Multi-user isolation
    """

    @staticmethod
    def extract_memories(
        message: str,
        user_id: str,
        message_id: str,
        current_time: Optional[datetime] = None,
        llm_callable: Optional[Callable[[str], str]] = None,
    ) -> List[MemoryCandidate]:
        """Extracts structured memory candidates from a user message."""
        return extract_memories(
            message=message,
            user_id=user_id,
            source_message_id=message_id,
            current_time=current_time,
            llm_callable=llm_callable,
        )

    @staticmethod
    def detect_conflicts(
        candidate: MemoryCandidate,
        existing_memories: List[Memory],
    ) -> List[ConflictResult]:
        """Detects contradictions, duplicates, temporal updates, or explicit forgets."""
        return detect_conflicts(candidate=candidate, existing_memories=existing_memories)

    @staticmethod
    def resolve_conflict(
        conflict: ConflictResult,
        current_time: Optional[datetime] = None,
    ) -> ResolutionPlan:
        """Executes state transitions to resolve a detected conflict."""
        return resolve_conflict(conflict=conflict, current_time=current_time)

    @staticmethod
    def calculate_confidence(memory: Memory, boost_rate: float = 0.15) -> float:
        """Reinforces confidence for confirmed memories."""
        return reinforce_confidence(memory.confidence, boost_rate=boost_rate)

    @staticmethod
    def calculate_decay(memory: Memory, current_time: datetime) -> Memory:
        """Applies half-life decay and expiration to stale memories."""
        return apply_decay(memory=memory, current_time=current_time)

    @staticmethod
    def retrieve_memory_state(
        memories: List[Memory],
        user_id: str,
        target_time: Optional[datetime] = None,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        include_superseded: bool = False,
    ) -> List[Memory]:
        """
        Retrieves valid memories for a user, optionally point-in-time and filtered.
        Strictly isolates memory by user_id and filters out forgotten memories.
        """
        # Multi-user isolation
        user_memories = [m for m in memories if m.user_id == user_id and m.status != MemoryStatus.FORGOTTEN]

        if target_time:
            point_in_time = filter_timeline_at(
                user_memories,
                target_time=target_time,
                subject=subject,
                predicate=predicate,
            )
            return point_in_time

        # Current state
        results = []
        for mem in user_memories:
            if not include_superseded and mem.status != MemoryStatus.ACTIVE:
                continue
            if subject and mem.subject.lower() != subject.lower():
                continue
            if predicate and mem.predicate.lower() != predicate.lower():
                continue
            results.append(mem)

        return results

    @classmethod
    def process_message(
        cls,
        message: str,
        user_id: str,
        message_id: str,
        existing_memories: List[Memory],
        current_time: Optional[datetime] = None,
        llm_callable: Optional[Callable[[str], str]] = None,
    ) -> ResolutionPlan:
        """
        End-to-end pipeline:
        Message -> Candidates -> Conflict Check -> Resolution Plan
        """
        now = current_time or datetime.utcnow()
        candidates = cls.extract_memories(
            message=message,
            user_id=user_id,
            message_id=message_id,
            current_time=now,
            llm_callable=llm_callable,
        )

        all_to_add: List[Memory] = []
        all_to_update: List[Memory] = []
        explanations: List[str] = []

        # Track existing memories plus whatever we update in this batch
        working_existing = {m.id: m.copy(deep=True) for m in existing_memories if m.user_id == user_id}

        for cand in candidates:
            conflicts = cls.detect_conflicts(cand, list(working_existing.values()))
            for conf in conflicts:
                plan = cls.resolve_conflict(conf, current_time=now)
                all_to_add.extend(plan.memories_to_add)
                for updated in plan.memories_to_update:
                    all_to_update.append(updated)
                    working_existing[updated.id] = updated
                if plan.explanation:
                    explanations.append(plan.explanation)

        return ResolutionPlan(
            memories_to_add=all_to_add,
            memories_to_update=all_to_update,
            explanation="; ".join(explanations) if explanations else "Processed message.",
        )

