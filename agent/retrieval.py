from typing import List
from datetime import datetime

from agent.models import MemoryRecord, QueryPlan, RetrievalResult
from agent.interfaces import MemoryRepository, EmbeddingProvider
from agent.reranker import Reranker


class RetrievalPipeline:
    def __init__(
        self,
        repository: MemoryRepository,
        embedding_provider: EmbeddingProvider,
        reranker: Reranker,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.reranker = reranker

    def retrieve(
        self,
        user_id: str,
        query: str,
        query_plan: QueryPlan,
        reference_time: datetime,
        limit: int = 10,
    ) -> List[RetrievalResult]:
        # 1. Generate query embedding
        query_embedding = self.embedding_provider.get_embedding(query)

        # 2. Ask MemoryRepository for candidates
        candidates = self.repository.search(user_id, query_embedding, limit=50)

        # 3. Ensure candidates are user-scoped (Hard Filter)
        valid_candidates: List[MemoryRecord] = []
        for mem in candidates:
            if mem.user_id != user_id:
                continue
            valid_candidates.append(mem)

        # 4 & 5. Hard filtering (temporality, forgotten) and soft ranking
        # are handled by the existing Phase 1 Reranker contract.
        results = self.reranker.rerank(
            query_plan=query_plan,
            candidates=valid_candidates,
            query_time=reference_time,
            max_results=limit,
        )

        # 5.5 Drop irrelevant candidates (score too low)
        threshold = self.reranker.config.relevance_threshold
        results = [r for r in results if r.score >= threshold]

        # 6. Return ordered RetrievalResults
        return results
