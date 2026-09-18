from abc import ABC, abstractmethod
from typing import List, Optional

from .models import MemoryRecord


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> str:
        """Generate a text response from the LLM."""


class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Return an embedding vector for *text*."""


class MemoryRepository(ABC):
    """Persistence interface for memory records.

    Implementations must ensure that ``get_all`` filters by
    ``user_id`` at the storage level — the agent layer relies on
    this for user-isolation.
    """

    @abstractmethod
    def save(self, memory: MemoryRecord) -> None:
        """Persist *memory* (insert or update)."""

    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """Retrieve a single memory by its ID, or ``None``."""

    @abstractmethod
    def get_all(self, user_id: str) -> List[MemoryRecord]:
        """Retrieve all memories belonging to *user_id*."""
