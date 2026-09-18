import os
import sys
from datetime import datetime

from agent.models import MemoryRecord, MemoryStatus, RankingConfig
from agent.providers.fakes import (
    FakeMemoryRepository,
    FakeEmbeddingProvider,
    FakeLLMProvider,
)
from agent.query_planner import DeterministicQueryPlanner
from agent.reranker import Reranker
from agent.retrieval import RetrievalPipeline
from agent.context import ContextBuilder
from agent.orchestrator import Agent


def run_demo():
    print("==================================================")
    print("EPOQUESQUE TEMPORAL MEMORY ENGINE - FINAL DEMO")
    print("==================================================\n")

    # 1. Initialize deterministic fakes
    repo = FakeMemoryRepository()

    # 3D Orthogonal Embeddings logic extended:
    vec_current_q = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    vec_hist_q = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    vec_time_q = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
    vec_contra_q = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    vec_forgot_q = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    vec_iso_q = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    vec_irrel_q = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]

    embeddings = FakeEmbeddingProvider(embeddings={
        "What programming language am I currently using?": vec_current_q,
        "What was I using before C++?": vec_hist_q,
        "How did my language preference change?": vec_time_q,
        "What is my favorite animal?": vec_contra_q,
        "What is my secret code?": vec_forgot_q,
        "What is User 2's project?": vec_iso_q,
        
        # Memory Content embeddings:
        "Python": [0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "Java": [0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "C++": [1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        "Dog": vec_contra_q,
        "Cat": vec_contra_q,
        "Code123": vec_forgot_q,
        "ProjectX": vec_iso_q,
    })

    llm = FakeLLMProvider()
    config = RankingConfig(relevance_threshold=0.45)
    reranker = Reranker(embeddings, config)
    retrieval = RetrievalPipeline(repo, embeddings, reranker)
    planner = DeterministicQueryPlanner()
    context_builder = ContextBuilder()
    
    agent = Agent(llm, planner, retrieval, context_builder)

    print("Step 1: Ingesting Temporal Memories (Python -> Java -> C++)")
    repo.save(MemoryRecord(
        id="mem_01_python", user_id="user_1", subject="User", predicate="uses", object="Python",
        memory_type="preference", content="Python", confidence=1.0,
        status=MemoryStatus.SUPERSEDED, valid_from=datetime(2025, 1, 1), valid_until=datetime(2026, 1, 1),
        created_at=datetime(2025, 1, 1), updated_at=datetime(2025, 1, 1)
    ))
    repo.save(MemoryRecord(
        id="mem_02_java", user_id="user_1", subject="User", predicate="uses", object="Java",
        memory_type="preference", content="Java", confidence=1.0,
        status=MemoryStatus.SUPERSEDED, valid_from=datetime(2026, 1, 1), valid_until=datetime(2026, 4, 1),
        created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
    ))
    repo.save(MemoryRecord(
        id="mem_03_cpp", user_id="user_1", subject="User", predicate="uses", object="C++",
        memory_type="preference", content="C++", confidence=1.0,
        status=MemoryStatus.ACTIVE, valid_from=datetime(2026, 4, 1),
        created_at=datetime(2026, 4, 1), updated_at=datetime(2026, 4, 1)
    ))

    print("Step 2: Ingesting Contradictory Memories (Cat & Dog)")
    repo.save(MemoryRecord(
        id="mem_contra_dog", user_id="user_1", subject="User", predicate="likes", object="Dog",
        memory_type="preference", content="Dog", confidence=1.0, status=MemoryStatus.ACTIVE,
        valid_from=datetime(2026, 1, 1), created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
    ))
    repo.save(MemoryRecord(
        id="mem_contra_cat", user_id="user_1", subject="User", predicate="likes", object="Cat",
        memory_type="preference", content="Cat", confidence=1.0, status=MemoryStatus.ACTIVE,
        valid_from=datetime(2026, 2, 1), created_at=datetime(2026, 2, 1), updated_at=datetime(2026, 2, 1)
    ))

    print("Step 3: Ingesting Forgotten Memory (Code123)")
    repo.save(MemoryRecord(
        id="mem_forgotten", user_id="user_1", subject="User", predicate="has", object="Code123",
        memory_type="fact", content="Code123", confidence=1.0, status=MemoryStatus.FORGOTTEN,
        valid_from=datetime(2026, 1, 1), created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
    ))

    print("Step 4: Ingesting Memory for User 2 (ProjectX)")
    repo.save(MemoryRecord(
        id="mem_isolated", user_id="user_2", subject="User", predicate="has", object="ProjectX",
        memory_type="fact", content="ProjectX", confidence=1.0, status=MemoryStatus.ACTIVE,
        valid_from=datetime(2026, 1, 1), created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
    ))

    ref_time = datetime(2026, 9, 18, 10, 0, 0)
    print("\n--- BEGIN DEMO QUERIES ---\n")

    def query_agent(desc: str, query: str, user_id: str = "user_1"):
        print(f"Scenario: {desc}")
        print(f"User '{user_id}': \"{query}\"")
        resp = agent.run(user_id=user_id, query=query, reference_time=ref_time)
        print(f"Agent Source IDs: {[s.memory_id for s in resp.sources]}")
        print(f"Agent Conflict:   {resp.conflict_detected}")
        print(f"Agent Provenance: {resp.sources[0].reason if resp.sources else 'None'}")
        print("-" * 50)

    query_agent(
        "Current Temporal Query",
        "What programming language am I currently using?"
    )

    query_agent(
        "Historical Temporal Query",
        "What was I using before C++?"
    )

    query_agent(
        "Timeline Query",
        "How did my language preference change?"
    )

    query_agent(
        "Contradiction Query",
        "What is my favorite animal?"
    )

    query_agent(
        "Forgotten Memory Exclusion",
        "What is my secret code?"
    )

    query_agent(
        "User Isolation",
        "What is User 2's project?",
        user_id="user_1"
    )

    print("\nDEMO COMPLETE")


if __name__ == "__main__":
    run_demo()

