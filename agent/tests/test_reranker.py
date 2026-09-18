"""Tests for the Reranker — filtering and scoring logic."""
import pytest
from datetime import datetime

from agent.models import (
    MemoryRecord,
    MemoryStatus,
    QueryPlan,
    QueryType,
    RankingConfig,
)
from agent.providers.fakes import FakeEmbeddingProvider
from agent.reranker import Reranker, is_temporally_current


# ── Fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def base_memory():
    return MemoryRecord(
        id="base",
        user_id="user1",
        subject="I",
        predicate="use",
        object="Python",
        memory_type="fact",
        content="I use Python",
        confidence=1.0,
        status=MemoryStatus.ACTIVE,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
    )


@pytest.fixture
def reranker():
    embeddings = {
        "Query": [1.0, 0.0, 0.0],
        "High Semantic": [0.9, 0.1, 0.0],
        "Low Semantic": [0.0, 1.0, 0.0],
    }
    return Reranker(
        FakeEmbeddingProvider(embeddings), RankingConfig()
    )


QUERY_TIME = datetime(2023, 6, 1, 12, 0, 0)


def _current_plan(query: str = "Query") -> QueryPlan:
    return QueryPlan(
        query_type=QueryType.CURRENT, search_query=query
    )


def _historical_plan(query: str = "Query") -> QueryPlan:
    return QueryPlan(
        query_type=QueryType.HISTORICAL, search_query=query
    )


def _timeline_plan(query: str = "Query") -> QueryPlan:
    return QueryPlan(
        query_type=QueryType.TIMELINE, search_query=query
    )


# ── is_temporally_current unit tests ─────────────────────────────

class TestIsTemporallyCurrent:
    """Direct tests for the extracted helper function."""

    def test_active_no_bounds(self, base_memory):
        assert is_temporally_current(base_memory, QUERY_TIME)

    def test_active_within_bounds(self, base_memory):
        mem = base_memory.model_copy(update={
            "valid_from": datetime(2023, 1, 1),
            "valid_until": datetime(2024, 1, 1),
        })
        assert is_temporally_current(mem, QUERY_TIME)

    def test_active_expired(self, base_memory):
        mem = base_memory.model_copy(update={
            "valid_until": datetime(2023, 5, 1),
        })
        assert not is_temporally_current(mem, QUERY_TIME)

    def test_active_future(self, base_memory):
        mem = base_memory.model_copy(update={
            "valid_from": datetime(2023, 7, 1),
        })
        assert not is_temporally_current(mem, QUERY_TIME)

    def test_active_no_valid_from(self, base_memory):
        """valid_from=None means unbounded start."""
        mem = base_memory.model_copy(update={
            "valid_until": datetime(2024, 1, 1),
        })
        assert is_temporally_current(mem, QUERY_TIME)

    def test_active_no_valid_until(self, base_memory):
        """valid_until=None means unbounded end."""
        mem = base_memory.model_copy(update={
            "valid_from": datetime(2023, 1, 1),
        })
        assert is_temporally_current(mem, QUERY_TIME)

    def test_exact_valid_until_boundary(self, base_memory):
        """valid_until == query_time → excluded (half-open)."""
        mem = base_memory.model_copy(update={
            "valid_until": QUERY_TIME,
        })
        assert not is_temporally_current(mem, QUERY_TIME)

    def test_exact_valid_from_boundary(self, base_memory):
        """valid_from == query_time → included."""
        mem = base_memory.model_copy(update={
            "valid_from": QUERY_TIME,
        })
        assert is_temporally_current(mem, QUERY_TIME)

    def test_superseded_not_current(self, base_memory):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.SUPERSEDED,
        })
        assert not is_temporally_current(mem, QUERY_TIME)

    def test_forgotten_not_current(self, base_memory):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.FORGOTTEN,
        })
        assert not is_temporally_current(mem, QUERY_TIME)


# ── Hard filter tests via reranker ───────────────────────────────

class TestCurrentQueryFiltering:
    def test_active_valid_included(self, reranker, base_memory):
        results = reranker.rerank(
            _current_plan(), [base_memory], QUERY_TIME
        )
        assert len(results) == 1

    def test_expired_excluded(self, reranker, base_memory):
        mem = base_memory.model_copy(update={
            "valid_until": datetime(2023, 5, 1),
        })
        results = reranker.rerank(
            _current_plan(), [mem], QUERY_TIME
        )
        assert len(results) == 0

    def test_future_excluded(self, reranker, base_memory):
        mem = base_memory.model_copy(update={
            "valid_from": datetime(2023, 7, 1),
        })
        results = reranker.rerank(
            _current_plan(), [mem], QUERY_TIME
        )
        assert len(results) == 0

    def test_superseded_excluded(self, reranker, base_memory):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.SUPERSEDED,
        })
        results = reranker.rerank(
            _current_plan(), [mem], QUERY_TIME
        )
        assert len(results) == 0


class TestHistoricalQueryFiltering:
    def test_superseded_included(self, reranker, base_memory):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.SUPERSEDED,
        })
        results = reranker.rerank(
            _historical_plan(), [mem], QUERY_TIME
        )
        assert len(results) == 1

    def test_expired_included(self, reranker, base_memory):
        mem = base_memory.model_copy(update={
            "valid_until": datetime(2023, 5, 1),
        })
        results = reranker.rerank(
            _historical_plan(), [mem], QUERY_TIME
        )
        assert len(results) == 1


class TestForgottenMemoryFiltering:
    def test_forgotten_excluded_from_current(
        self, reranker, base_memory
    ):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.FORGOTTEN,
        })
        assert len(reranker.rerank(
            _current_plan(), [mem], QUERY_TIME
        )) == 0

    def test_forgotten_excluded_from_historical(
        self, reranker, base_memory
    ):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.FORGOTTEN,
        })
        assert len(reranker.rerank(
            _historical_plan(), [mem], QUERY_TIME
        )) == 0

    def test_forgotten_excluded_from_timeline(
        self, reranker, base_memory
    ):
        mem = base_memory.model_copy(update={
            "status": MemoryStatus.FORGOTTEN,
        })
        assert len(reranker.rerank(
            _timeline_plan(), [mem], QUERY_TIME
        )) == 0


# ── Soft ranking tests ───────────────────────────────────────────

class TestConfidenceRanking:
    def test_higher_confidence_ranks_first(
        self, reranker, base_memory
    ):
        mem1 = base_memory.model_copy(
            update={"id": "low", "confidence": 0.5}
        )
        mem2 = base_memory.model_copy(
            update={"id": "high", "confidence": 1.0}
        )
        results = reranker.rerank(
            _current_plan(), [mem1, mem2], QUERY_TIME
        )
        assert results[0].memory.id == "high"
        assert results[1].memory.id == "low"


class TestSemanticRanking:
    def test_closer_embedding_ranks_first(
        self, reranker, base_memory
    ):
        mem_low = base_memory.model_copy(update={
            "id": "low", "content": "Low Semantic",
        })
        mem_high = base_memory.model_copy(update={
            "id": "high", "content": "High Semantic",
        })
        results = reranker.rerank(
            _current_plan(), [mem_low, mem_high], QUERY_TIME
        )
        assert results[0].memory.id == "high"


class TestTemporalRanking:
    def test_valid_beats_expired_on_historical(
        self, reranker, base_memory
    ):
        expired = base_memory.model_copy(update={
            "id": "expired",
            "valid_until": datetime(2023, 5, 1),
        })
        valid = base_memory.model_copy(update={"id": "valid"})
        results = reranker.rerank(
            _historical_plan(), [expired, valid], QUERY_TIME
        )
        assert results[0].memory.id == "valid"


class TestRecencyRanking:
    def test_recent_beats_old(self, reranker, base_memory):
        old = base_memory.model_copy(update={
            "id": "old",
            "updated_at": datetime(2022, 1, 1),
        })
        recent = base_memory.model_copy(update={
            "id": "recent",
            "updated_at": datetime(2023, 5, 30),
        })
        results = reranker.rerank(
            _current_plan(), [old, recent], QUERY_TIME
        )
        assert results[0].memory.id == "recent"


class TestConfigurableWeights:
    def test_confidence_weight_dominates(self, base_memory):
        provider = FakeEmbeddingProvider()
        mem_high_conf = base_memory.model_copy(update={
            "id": "hc",
            "confidence": 1.0,
            "updated_at": datetime(2022, 1, 1),
        })
        mem_low_conf = base_memory.model_copy(update={
            "id": "lc",
            "confidence": 0.1,
            "updated_at": datetime(2023, 5, 30),
        })
        config = RankingConfig(
            semantic_weight=0.0,
            confidence_weight=1.0,
            temporal_weight=0.0,
            recency_weight=0.0,
        )
        r = Reranker(provider, config)
        results = r.rerank(
            _current_plan(), [mem_high_conf, mem_low_conf],
            QUERY_TIME,
        )
        assert results[0].memory.id == "hc"

    def test_recency_weight_dominates(self, base_memory):
        provider = FakeEmbeddingProvider()
        mem_old = base_memory.model_copy(update={
            "id": "old",
            "confidence": 1.0,
            "updated_at": datetime(2022, 1, 1),
        })
        mem_new = base_memory.model_copy(update={
            "id": "new",
            "confidence": 0.1,
            "updated_at": datetime(2023, 5, 30),
        })
        config = RankingConfig(
            semantic_weight=0.0,
            confidence_weight=0.0,
            temporal_weight=0.0,
            recency_weight=1.0,
        )
        r = Reranker(provider, config)
        results = r.rerank(
            _current_plan(), [mem_old, mem_new], QUERY_TIME,
        )
        assert results[0].memory.id == "new"


# ── Timeline ordering ────────────────────────────────────────────

class TestTimelineOrdering:
    def test_chronological_order(self, reranker, base_memory):
        mem1 = base_memory.model_copy(update={
            "id": "m1",
            "created_at": datetime(2021, 1, 1),
            "updated_at": datetime(2021, 1, 1),
        })
        mem2 = base_memory.model_copy(update={
            "id": "m2",
            "created_at": datetime(2023, 1, 1),
            "updated_at": datetime(2023, 1, 1),
        })
        mem3 = base_memory.model_copy(update={
            "id": "m3",
            "created_at": datetime(2022, 1, 1),
            "updated_at": datetime(2022, 1, 1),
        })
        results = reranker.rerank(
            _timeline_plan(), [mem1, mem2, mem3], QUERY_TIME
        )
        assert len(results) == 3
        assert results[0].memory.id == "m1"
        assert results[1].memory.id == "m3"
        assert results[2].memory.id == "m2"


# ── User isolation via FakeMemoryRepository ──────────────────────

class TestUserIsolationInRepository:
    def test_get_all_filters_by_user_id(self):
        from agent.providers.fakes import FakeMemoryRepository
        repo = FakeMemoryRepository()

        mem_a = base_mem("a", "alice")
        mem_b = base_mem("b", "bob")
        repo.save(mem_a)
        repo.save(mem_b)

        assert [m.id for m in repo.get_all("alice")] == ["a"]
        assert [m.id for m in repo.get_all("bob")] == ["b"]
        assert repo.get_all("charlie") == []


def base_mem(mid: str, uid: str) -> MemoryRecord:
    return MemoryRecord(
        id=mid,
        user_id=uid,
        subject="s",
        predicate="p",
        object="o",
        memory_type="fact",
        content="c",
        confidence=0.9,
        status=MemoryStatus.ACTIVE,
        created_at=datetime(2023, 1, 1),
        updated_at=datetime(2023, 1, 1),
    )
