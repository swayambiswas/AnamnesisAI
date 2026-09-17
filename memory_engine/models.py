from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    ARCHIVED = "archived"
    FORGOTTEN = "forgotten"


class MemoryType(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    GOAL = "goal"
    RELATIONSHIP = "relationship"
    LOCATION = "location"
    SKILL = "skill"
    PROJECT = "project"
    EVENT = "event"


class ConflictType(str, Enum):
    NONE = "none"
    DUPLICATE = "duplicate"
    CONTRADICTION = "contradiction"
    TEMPORAL_UPDATE = "temporal_update"
    EXPLICIT_FORGET = "explicit_forget"


class ResolutionAction(str, Enum):
    ADD_NEW = "add_new"
    REINFORCE_DUPLICATE = "reinforce_duplicate"
    SUPERSEDE = "supersede"
    KEEP_BOTH_TEMPORAL = "keep_both_temporal"
    FORGET = "forget"
    IGNORE = "ignore"


class Memory(BaseModel):
    id: str
    user_id: str
    subject: str
    predicate: str
    object_: str = Field(alias="object")
    memory_type: MemoryType
    confidence: float = Field(ge=0.0, le=1.0)
    status: MemoryStatus = MemoryStatus.ACTIVE
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    source_message_id: str
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    provenance_note: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

    def to_dict(self) -> Dict[str, Any]:
        d = self.dict(by_alias=True)
        # Convert enums to value if not already
        if isinstance(d.get("status"), Enum):
            d["status"] = d["status"].value
        if isinstance(d.get("memory_type"), Enum):
            d["memory_type"] = d["memory_type"].value
        return d


class MemoryCandidate(BaseModel):
    user_id: str
    subject: str
    predicate: str
    object_: str = Field(alias="object")
    memory_type: MemoryType
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source_message_id: str
    is_explicit_forget: bool = False
    is_weak_inference: bool = False
    raw_text: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class ConflictResult(BaseModel):
    conflict: bool
    conflict_type: ConflictType
    candidate: MemoryCandidate
    existing_memory_id: Optional[str] = None
    existing_memory: Optional[Memory] = None
    resolution: ResolutionAction
    explanation: str

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True


class ResolutionPlan(BaseModel):
    memories_to_add: List[Memory] = Field(default_factory=list)
    memories_to_update: List[Memory] = Field(default_factory=list)
    explanation: str

    class Config:
        allow_population_by_field_name = True

