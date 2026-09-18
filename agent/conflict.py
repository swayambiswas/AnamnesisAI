from typing import List, Dict, Tuple
from datetime import datetime

from agent.models import RetrievalResult
from agent.reranker import is_temporally_current


class ConflictDetector:
    """Detects contradictions among retrieved memory records."""

    @staticmethod
    def detect_conflicts(
        results: List[RetrievalResult], reference_time: datetime
    ) -> bool:
        """
        Detect if multiple ACTIVE and CURRENT memories share the same
        subject and predicate but have different objects.
        """
        active_current_mems = [
            r.memory for r in results
            if is_temporally_current(r.memory, reference_time)
        ]

        seen: Dict[Tuple[str, str], str] = {}
        for mem in active_current_mems:
            key = (mem.subject.lower(), mem.predicate.lower())
            val = mem.object.lower()

            if key in seen:
                if seen[key] != val:
                    return True
            else:
                seen[key] = val

        return False
