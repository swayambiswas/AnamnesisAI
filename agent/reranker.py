import math
from typing import List
from datetime import datetime

from agent.models import (
    MemoryRecord,
    MemoryStatus,
    QueryPlan,
    QueryType,
    RankingConfig,
    RetrievalResult,
)
from agent.interfaces import EmbeddingProvider


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


def is_temporally_current(
    memory: MemoryRecord, query_time: datetime
) -> bool:
    """Return True iff the memory is both active and temporally valid.

    Temporal validity uses a half-open interval: [valid_from, valid_until).
    Missing bounds are treated as unbounded (always valid on that side).
    """
    if memory.status != MemoryStatus.ACTIVE:
        return False
    if memory.valid_from is not None and memory.valid_from > query_time:
        return False
    if memory.valid_until is not None and query_time >= memory.valid_until:
        return False
    return True


class Reranker:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        config: RankingConfig,
    ):
        self.embedding_provider = embedding_provider
        self.config = config

    def rerank(
        self,
        query_plan: QueryPlan,
        candidates: List[MemoryRecord],
        query_time: datetime,
        max_results: int = 5,
    ) -> List[RetrievalResult]:
        query_embedding = self.embedding_provider.get_embedding(
            query_plan.search_query
        )
        scored: List[RetrievalResult] = []

        for memory in candidates:
            # ── Hard filter: forgotten memories are never returned ──
            if memory.status == MemoryStatus.FORGOTTEN:
                continue

            current = is_temporally_current(memory, query_time)

            # ── Hard filter by query type ──
            if query_plan.query_type == QueryType.CURRENT:
                if not current:
                    continue

            # HISTORICAL / TIMELINE: superseded and expired are
            # permitted (forgotten already excluded above).

            # ── Soft scoring ──
            mem_embedding = self.embedding_provider.get_embedding(
                memory.content
            )
            semantic_score = cosine_similarity(
                query_embedding, mem_embedding
            )

            confidence_score = memory.confidence

            is_valid_from = (
                memory.valid_from is None
                or memory.valid_from <= query_time
            )
            is_valid_until = (
                memory.valid_until is None
                or query_time < memory.valid_until
            )
            temporally_valid = is_valid_from and is_valid_until
            temporal_score = 1.0 if temporally_valid else 0.5

            age_days = (query_time - memory.updated_at).days
            recency_score = math.exp(-0.01 * max(0, age_days))

            total_score = (
                semantic_score * self.config.semantic_weight
                + confidence_score * self.config.confidence_weight
                + temporal_score * self.config.temporal_weight
                + recency_score * self.config.recency_weight
            )

            scored.append(RetrievalResult(
                memory=memory,
                score=total_score,
                relevance_explanation=(
                    f"Semantic: {semantic_score:.2f}, "
                    f"Confidence: {confidence_score:.2f}, "
                    f"Temporal: {temporal_score:.2f}, "
                    f"Recency: {recency_score:.2f}"
                ),
            ))

        scored.sort(key=lambda x: x.score, reverse=True)
        results = scored[:max_results]

        if query_plan.query_type == QueryType.TIMELINE:
            results.sort(key=lambda x: x.memory.created_at)

        return results
