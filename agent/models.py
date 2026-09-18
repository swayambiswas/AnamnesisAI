from enum import Enum

from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    FORGOTTEN = "forgotten"


class MemoryRecord(BaseModel):
    id: str
    user_id: str
    subject: str
    predicate: str
    object: str
    memory_type: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    status: MemoryStatus
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    source_message_id: Optional[str] = None
    supersedes: Optional[str] = None

    @model_validator(mode="after")
    def check_temporal_consistency(self) -> "MemoryRecord":
        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_from >= self.valid_until
        ):
            raise ValueError(
                "valid_from must be strictly before valid_until"
            )
        return self


class QueryType(str, Enum):
    CURRENT = "current"
    HISTORICAL = "historical"
    TIMELINE = "timeline"
    GENERAL = "general"
    AMBIGUOUS = "ambiguous"


class QueryPlan(BaseModel):
    query_type: QueryType
    extracted_subjects: List[str] = Field(default_factory=list)
    extracted_predicates: List[str] = Field(default_factory=list)
    extracted_objects: List[str] = Field(default_factory=list)
    search_query: str = ""


class RankingConfig(BaseModel):
    semantic_weight: float = 0.7
    confidence_weight: float = 0.1
    temporal_weight: float = 0.1
    recency_weight: float = 0.1
    relevance_threshold: float = 0.45


class RetrievalResult(BaseModel):
    memory: MemoryRecord
    score: float
    relevance_explanation: Optional[str] = None


class Provenance(BaseModel):
    memory_id: str
    reason: List[str]
    confidence: float
    status: str


class AgentResponse(BaseModel):
    answer: str
    sources: List[Provenance] = Field(default_factory=list)
    uncertainty: bool = False
    conflict_detected: bool = False
