from typing import List

from agent.interfaces import EmbeddingProvider


class NotImplementedEmbeddingProvider(EmbeddingProvider):
    """Placeholder — concrete embedding provider comes in Phase 2+."""

    def get_embedding(self, text: str) -> List[float]:
        raise NotImplementedError(
            "Concrete Embedding provider is not implemented "
            "in Phase 1."
        )
