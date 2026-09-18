"""Tests for Agent orchestration."""
from datetime import datetime
from agent.orchestrator import Agent
from agent.providers.fakes import (
    FakeLLMProvider, FakeEmbeddingProvider, FakeMemoryRepository
)
from agent.query_planner import DeterministicQueryPlanner
from agent.retrieval import RetrievalPipeline
from agent.reranker import Reranker
from agent.models import RankingConfig, MemoryRecord, MemoryStatus
from agent.context import ContextBuilder


def test_agent_run_empty():
    repo = FakeMemoryRepository()
    llm = FakeLLMProvider(responses={})
    embeddings = FakeEmbeddingProvider()
    reranker = Reranker(embeddings, RankingConfig())
    retrieval = RetrievalPipeline(repo, embeddings, reranker)
    planner = DeterministicQueryPlanner()
    agent = Agent(llm, planner, retrieval, ContextBuilder())

    response = agent.run(
        "u1", "What is my favorite language?", datetime(2026, 1, 1)
    )

    assert response.uncertainty is True
    assert response.conflict_detected is False
    assert len(response.sources) == 0
    assert response.answer == "Fake LLM Response"


def test_agent_run_with_results():
    repo = FakeMemoryRepository()
    ref = datetime(2026, 1, 1)
    mem = MemoryRecord(
        id="1", user_id="u1", subject="I", predicate="use", object="Python",
        memory_type="fact", content="I use Python", confidence=1.0,
        status=MemoryStatus.ACTIVE, created_at=ref, updated_at=ref
    )
    repo.save(mem)

    llm = FakeLLMProvider(responses={})
    embeddings = FakeEmbeddingProvider()
    reranker = Reranker(embeddings, RankingConfig())
    retrieval = RetrievalPipeline(repo, embeddings, reranker)
    planner = DeterministicQueryPlanner()
    agent = Agent(llm, planner, retrieval, ContextBuilder())

    response = agent.run("u1", "What do I use?", ref)

    assert response.uncertainty is False
    assert response.conflict_detected is False
    assert len(response.sources) == 1
    assert response.sources[0].memory_id == "1"
    assert response.answer == "Fake LLM Response"
