from typing import List

from agent.models import RetrievalResult


class ProvenanceManager:
    @staticmethod
    def generate_provenance(results: List[RetrievalResult]) -> List[str]:
        """Extract unique memory IDs from retrieval results.

        These IDs represent the exact memories that were provided to
        the LLM in the context.  Order is preserved; duplicates are
        removed (keeping first occurrence).
        """
        seen: set[str] = set()
        ids: list[str] = []
        for result in results:
            mid = result.memory.id
            if mid not in seen:
                seen.add(mid)
                ids.append(mid)
        return ids
