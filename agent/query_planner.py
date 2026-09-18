import re
from agent.models import QueryPlan, QueryType


class DeterministicQueryPlanner:
    """Keyword-based query planner for deterministic classification.

    Intentionally simple: an LLM-assisted planner can replace or
    augment this by implementing the same ``plan()`` interface.
    """

    # Patterns are checked in priority order (first match wins).
    _TIMELINE_PATTERN = re.compile(
        r"\b(change(?:d)?|over time|history of|timeline|"
        r"show me the history)\b",
        re.IGNORECASE,
    )
    _HISTORICAL_PATTERN = re.compile(
        r"\b(before|previously|used to|past|historical|did i)\b",
        re.IGNORECASE,
    )
    _CURRENT_PATTERN = re.compile(
        r"\b(currently|current(?:ly)?|right now|using now|do i currently)\b",
        re.IGNORECASE,
    )
    _GENERAL_PATTERN = re.compile(
        r"\b(what do you remember|tell me about|what are my|list my)\b",
        re.IGNORECASE,
    )

    def plan(self, query: str) -> QueryPlan:
        query_lower = query.lower()

        if self._TIMELINE_PATTERN.search(query_lower):
            q_type = QueryType.TIMELINE
        elif self._HISTORICAL_PATTERN.search(query_lower):
            q_type = QueryType.HISTORICAL
        elif self._CURRENT_PATTERN.search(query_lower):
            q_type = QueryType.CURRENT
        elif self._GENERAL_PATTERN.search(query_lower):
            q_type = QueryType.GENERAL
        else:
            q_type = QueryType.AMBIGUOUS

        subjects: list[str] = []
        if "projects" in query_lower:
            subjects.append("projects")

        return QueryPlan(
            query_type=q_type,
            search_query=query,
            extracted_subjects=subjects,
        )
