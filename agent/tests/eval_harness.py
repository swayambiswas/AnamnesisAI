import sys
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from agent.models import MemoryRecord, MemoryStatus
from agent.interfaces import MemoryRepository
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
from agent.models import RankingConfig


class EvalCase(BaseModel):
    name: str
    query: str
    reference_time: datetime
    user_id: str
    expected_memory_ids: List[str]
    expected_conflict: bool = False
    expected_uncertainty: Optional[bool] = None


class EvalReport(BaseModel):
    case_name: str
    query: str
    reference_time: str
    expected_memory_ids: List[str]
    actual_memory_ids: List[str]
    pass_status: str
    reason: str


class EvalHarness:
    def __init__(self, repository: MemoryRepository, agent: Agent):
        self.repository = repository
        self.agent = agent
        self.reports: List[EvalReport] = []

    def setup_memories(self, memories: List[MemoryRecord]):
        for mem in memories:
            self.repository.save(mem)

    def evaluate_case(self, case: EvalCase) -> bool:
        response = self.agent.run(
            user_id=case.user_id,
            query=case.query,
            reference_time=case.reference_time,
        )

        retrieved_ids = [src.memory_id for src in response.sources]

        success = True
        reasons = []

        if retrieved_ids != case.expected_memory_ids:
            reasons.append(
                f"Memory mismatch: Expected {
                    case.expected_memory_ids}, Got {retrieved_ids}")
            success = False

        if response.conflict_detected != case.expected_conflict:
            reasons.append(
                f"Conflict mismatch: Expected {
                    case.expected_conflict}, Got {
                    response.conflict_detected}")
            success = False

        if case.expected_uncertainty is not None and response.uncertainty != case.expected_uncertainty:  # noqa: E501
            reasons.append(
                f"Uncertainty mismatch: Expected {
                    case.expected_uncertainty}, Got {
                    response.uncertainty}")
            success = False

        if success:
            reasons.append("All assertions passed.")
            print(f"[PASS] {case.name}")
        else:
            print(f"[FAIL] {case.name} - {reasons}")

        self.reports.append(EvalReport(
            case_name=case.name,
            query=case.query,
            reference_time=case.reference_time.isoformat(),
            expected_memory_ids=case.expected_memory_ids,
            actual_memory_ids=retrieved_ids,
            pass_status="PASS" if success else "FAIL",
            reason="; ".join(reasons)
        ))

        return success

    def write_markdown_report(self, path: str):
        with open(path, "w") as f:
            f.write("# Phase 2B Retrieval Evaluation Report\n\n")
            f.write("Generated at: " + datetime.now().isoformat() + "\n\n")
            f.write("## Evaluation Cases\n\n")

            for report in self.reports:
                f.write(f"### {report.case_name}\n")
                f.write(f"- **Query**: `{report.query}`\n")
                f.write(f"- **Reference Time**: `{report.reference_time}`\n")
                f.write(
                    f"- **Expected IDs**: `{report.expected_memory_ids}`\n")
                f.write(f"- **Actual IDs**: `{report.actual_memory_ids}`\n")
                f.write(f"- **Result**: `{report.pass_status}`\n")
                f.write(f"- **Reason**: {report.reason}\n\n")


def run_evaluations():
    repo = FakeMemoryRepository()

    # 3D Orthogonal Embeddings logic extended:
    # 0 -> current query
    # 1 -> historical query
    # 2 -> timeline query
    # 3 -> contradiction query
    # 4 -> forgotten query
    # 5 -> isolated query
    # 6 -> irrelevant query

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
        "What is the user's project?": vec_iso_q,
        "What color is the sky?": vec_irrel_q,

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

    config = RankingConfig()
    reranker = Reranker(embeddings, config)
    retrieval = RetrievalPipeline(repo, embeddings, reranker)
    planner = DeterministicQueryPlanner()
    context_builder = ContextBuilder()

    agent = Agent(llm, planner, retrieval, context_builder)

    harness = EvalHarness(repo, agent)

    memories = [
        # Narrative 1: Programming Languages
        MemoryRecord(
            id="mem_01_python", user_id="user_1", subject="User", predicate="uses", object="Python",  # noqa: E501
            memory_type="preference", content="Python", confidence=1.0,
            status=MemoryStatus.SUPERSEDED, valid_from=datetime(2025, 1, 1), valid_until=datetime(2026, 1, 1),  # noqa: E501
            created_at=datetime(2025, 1, 1), updated_at=datetime(2025, 1, 1)
        ),
        MemoryRecord(
            id="mem_02_java", user_id="user_1", subject="User", predicate="uses", object="Java",  # noqa: E501
            memory_type="preference", content="Java", confidence=1.0,
            status=MemoryStatus.SUPERSEDED, valid_from=datetime(2026, 1, 1), valid_until=datetime(2026, 4, 1),  # noqa: E501
            created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
        ),
        MemoryRecord(
            id="mem_03_cpp", user_id="user_1", subject="User", predicate="uses", object="C++",  # noqa: E501
            memory_type="preference", content="C++", confidence=1.0,
            status=MemoryStatus.ACTIVE, valid_from=datetime(2026, 4, 1),
            created_at=datetime(2026, 4, 1), updated_at=datetime(2026, 4, 1)
        ),

        # Contradiction: Two active memories sharing same subject/predicate but
        # different objects
        MemoryRecord(
            id="mem_contra_dog", user_id="user_1", subject="User", predicate="likes", object="Dog",  # noqa: E501
            memory_type="preference", content="Dog", confidence=1.0,
            status=MemoryStatus.ACTIVE, valid_from=datetime(2026, 1, 1),
            created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
        ),
        MemoryRecord(
            id="mem_contra_cat", user_id="user_1", subject="User", predicate="likes", object="Cat",  # noqa: E501
            memory_type="preference", content="Cat", confidence=1.0,
            status=MemoryStatus.ACTIVE, valid_from=datetime(2026, 2, 1),
            created_at=datetime(2026, 2, 1), updated_at=datetime(2026, 2, 1)
        ),

        # Forgotten Memory
        MemoryRecord(
            id="mem_forgotten", user_id="user_1", subject="User", predicate="has", object="Code123",  # noqa: E501
            memory_type="fact", content="Code123", confidence=1.0,
            status=MemoryStatus.FORGOTTEN, valid_from=datetime(2026, 1, 1),
            created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
        ),

        # User Isolation: A high-relevance memory belonging to someone else
        MemoryRecord(
            id="mem_isolated", user_id="user_2", subject="User", predicate="has", object="ProjectX",  # noqa: E501
            memory_type="fact", content="ProjectX", confidence=1.0,
            status=MemoryStatus.ACTIVE, valid_from=datetime(2026, 1, 1),
            created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
        )
    ]

    harness.setup_memories(memories)

    cases = [
        EvalCase(
            name="1. Current-state retrieval",
            query="What programming language am I currently using?",
            user_id="user_1",
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            expected_memory_ids=["mem_03_cpp"],
        ),
        EvalCase(
            name="2. Historical retrieval",
            query="What was I using before C++?",
            user_id="user_1",
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            expected_memory_ids=["mem_02_java"],
        ),
        EvalCase(
            name="3. Timeline retrieval (Order verified implicitly by ID array match)",  # noqa: E501
            query="How did my language preference change?",
            user_id="user_1",
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            expected_memory_ids=["mem_01_python", "mem_02_java", "mem_03_cpp"],  # noqa: E501
        ),
        EvalCase(
            name="4. Contradiction handling",
            query="What is my favorite animal?",
            user_id="user_1",
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            # Expected to retrieve both
            expected_memory_ids=["mem_contra_cat", "mem_contra_dog"],
            expected_conflict=True,
        ),
        EvalCase(
            name="5. Forgotten-memory exclusion",
            query="What is my secret code?",
            user_id="user_1",
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            expected_memory_ids=[],
            expected_uncertainty=True,
        ),
        EvalCase(
            name="6. User isolation",
            query="What is the user's project?",
            user_id="user_1",  # User 1 asking for it, but it belongs to user_2  # noqa: E501
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            expected_memory_ids=[],
            expected_uncertainty=True,
        ),
        EvalCase(
            name="7. Irrelevant-query rejection",
            query="What color is the sky?",
            user_id="user_1",
            reference_time=datetime(2026, 9, 18, 10, 0, 0),
            expected_memory_ids=[],
            expected_uncertainty=True,
        )
    ]

    all_passed = True
    for case in cases:
        if not harness.evaluate_case(case):
            all_passed = False

    harness.write_markdown_report("docs/phase2-evaluation.md")

    if all_passed:
        print("\nAll evaluation cases passed! Report written to docs/phase2-evaluation.md")  # noqa: E501
        sys.exit(0)
    else:
        print("\nSome evaluation cases failed. See docs/phase2-evaluation.md")
        sys.exit(1)


if __name__ == "__main__":
    run_evaluations()
