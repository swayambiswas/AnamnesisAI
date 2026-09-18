from typing import Optional

from agent.interfaces import LLMProvider


class NotImplementedLLMProvider(LLMProvider):
    """Placeholder — concrete Gemini provider comes in Phase 2+."""

    def generate(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> str:
        raise NotImplementedError(
            "Concrete LLM provider is not implemented in Phase 1."
        )
