import os
from typing import Optional

from google import genai
from google.genai import types

from agent.interfaces import LLMProvider


class NotImplementedLLMProvider(LLMProvider):
    """Placeholder ?" concrete Gemini provider comes in Phase 2+."""

    def generate(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> str:
        raise NotImplementedError(
            "Concrete LLM provider is not implemented in Phase 1."
        )


class GeminiLLMProvider(LLMProvider):
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.0,
    ):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature

    def generate(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> str:
        config = types.GenerateContentConfig(
            temperature=self.temperature
        )
        if system_instruction:
            config.system_instruction = system_instruction
            
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini LLM Provider failed: {e}")
