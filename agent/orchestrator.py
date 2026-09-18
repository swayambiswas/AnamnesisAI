from datetime import datetime

from agent.models import AgentResponse
from agent.interfaces import LLMProvider
from agent.query_planner import DeterministicQueryPlanner
from agent.retrieval import RetrievalPipeline
from agent.context import ContextBuilder
from agent.provenance import ProvenanceManager
from agent.conflict import ConflictDetector


class Agent:
    def __init__(
        self,
        llm_provider: LLMProvider,
        query_planner: DeterministicQueryPlanner,
        retrieval_pipeline: RetrievalPipeline,
        context_builder: ContextBuilder,
        system_instruction: str = "You are a helpful assistant.",
    ):
        self.llm_provider = llm_provider
        self.query_planner = query_planner
        self.retrieval_pipeline = retrieval_pipeline
        self.context_builder = context_builder
        self.system_instruction = system_instruction

    def run(
        self,
        user_id: str,
        query: str,
        reference_time: datetime,
    ) -> AgentResponse:
        # 1. Plan query
        plan = self.query_planner.plan(query)

        # 2. Retrieve candidates
        results = self.retrieval_pipeline.retrieve(
            user_id=user_id,
            query=query,
            query_plan=plan,
            reference_time=reference_time,
        )

        # 3. Detect conflicts
        conflict_detected = ConflictDetector.detect_conflicts(
            results, reference_time
        )

        # 4. Generate provenance
        sources = ProvenanceManager.generate_provenance(
            results, reference_time
        )

        # 5. Build context
        context = self.context_builder.build_context(
            results=results,
            system_instruction=self.system_instruction,
            user_query=query,
        )

        # 6. Generate answer
        answer = self.llm_provider.generate(
            prompt=context, system_instruction=self.system_instruction
        )

        # 7. Construct AgentResponse
        return AgentResponse(
            answer=answer,
            sources=sources,
            uncertainty=len(results) == 0,
            conflict_detected=conflict_detected,
        )
