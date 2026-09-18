import os
from typing import List

from google import genai

from agent.interfaces import EmbeddingProvider


class NotImplementedEmbeddingProvider(EmbeddingProvider):
    """Placeholder ?" concrete embedding provider comes in Phase 2+."""

    def get_embedding(self, text: str) -> List[float]:
        raise NotImplementedError(
            "Concrete Embedding provider is not implemented "
            "in Phase 1."
        )


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        model_name: str = "text-embedding-004",
    ):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
            )
            if not response.embeddings or not response.embeddings[0].values:
                raise ValueError("No embedding returned.")
            return response.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Gemini Embedding Provider failed: {e}")
