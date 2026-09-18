from typing import Dict, List, Optional

from agent.interfaces import (
    EmbeddingProvider,
    LLMProvider,
    MemoryRepository,
)
from agent.models import MemoryRecord


class FakeLLMProvider(LLMProvider):
    """Deterministic LLM stub for testing."""

    def __init__(
        self, responses: Optional[Dict[str, str]] = None
    ) -> None:
        self.responses: Dict[str, str] = responses or {}
        self.calls: List[Dict[str, Optional[str]]] = []

    def generate(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> str:
        self.calls.append(
            {"prompt": prompt, "system_instruction": system_instruction}
        )
        return self.responses.get(prompt, "Fake LLM Response")


class FakeEmbeddingProvider(EmbeddingProvider):
    """Deterministic embedding stub for testing.

    Returns pre-seeded vectors when the text matches a key in
    *embeddings*; otherwise returns ``default_embedding``.
    """

    def __init__(
        self,
        embeddings: Optional[Dict[str, List[float]]] = None,
    ) -> None:
        self.embeddings: Dict[str, List[float]] = embeddings or {}
        self.calls: List[str] = []
        self.default_embedding: List[float] = [0.0, 0.0, 1.0]

    def get_embedding(self, text: str) -> List[float]:
        self.calls.append(text)
        return self.embeddings.get(text, self.default_embedding)


class FakeMemoryRepository(MemoryRepository):
    """In-memory repository stub for testing."""

    def __init__(self) -> None:
        self.memories: Dict[str, MemoryRecord] = {}

    def save(self, memory: MemoryRecord) -> None:
        self.memories[memory.id] = memory

    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        return self.memories.get(memory_id)

    def get_all(self, user_id: str) -> List[MemoryRecord]:
        return [
            m for m in self.memories.values()
            if m.user_id == user_id
        ]

    def search(
        self, user_id: str, query_embedding: List[float], limit: int = 10
    ) -> List[MemoryRecord]:
        user_memories = self.get_all(user_id)
        return user_memories[:limit]
