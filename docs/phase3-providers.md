# Phase 3 - Real LLM and Embedding Providers

## Overview
Phase 3 brings real-world generative AI and vector embedding capabilities to the Epoquesque agent layer, replacing the deterministic offline fakes while preserving the strict architectural separation of concerns.

## Implemented Providers
The `google-genai` SDK was installed and implemented via `agent/providers/llm.py` and `agent/providers/embeddings.py`.

### GeminiLLMProvider
- **Adapter**: Maps `LLMProvider` contract (`generate`) to the `gemini-2.5-flash` model.
- **Configuration**: Loads credentials explicitly via `os.environ.get("GEMINI_API_KEY")`.
- **Security**: Fails fast (raises `ValueError`) if credentials are absent. The API key is never logged or included in prompt construction.
- **Resilience**: Wraps API calls in standard try/except blocks throwing localized `RuntimeError`.

### GeminiEmbeddingProvider
- **Adapter**: Maps `EmbeddingProvider` contract (`get_embedding`) to the `text-embedding-004` model.
- **Data Validation**: Enforces length and bounds checking on the resulting embedding array natively before passing it to the Reranker.

## Offline Preservation
The `FakeLLMProvider` and `FakeEmbeddingProvider` (with deterministic 3D orthogonal embeddings) remain fully intact and active in the test suite. The `pytest` suite does NOT require internet access or API keys, ensuring CI/CD systems and other engineers can run the test suite instantly without side-effects.

