from typing import List

from datetime import datetime

from agent.models import RetrievalResult, Provenance
from agent.reranker import is_temporally_current


class ProvenanceManager:
    @staticmethod
    def generate_provenance(
        results: List[RetrievalResult], reference_time: datetime
    ) -> List[Provenance]:
        """Extract unique provenance records from retrieval results."""
        seen: set[str] = set()
        provenance_list: List[Provenance] = []

        for result in results:
            mem = result.memory
            mid = mem.id
            if mid not in seen:
                seen.add(mid)

                reasons = ["semantic_match"]
                if is_temporally_current(mem, reference_time):
                    reasons.append("current_state_match")
                if mem.status == "active":
                    reasons.append("active_memory")

                prov = Provenance(
                    memory_id=mid,
                    reason=reasons,
                    confidence=mem.confidence,
                    status=mem.status.value,
                )
                provenance_list.append(prov)

        return provenance_list
