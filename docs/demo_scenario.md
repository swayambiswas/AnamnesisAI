# Epoquesque AI/Agent - Final Demo Scenario

This document demonstrates the full capabilities of the Epoquesque temporal memory engine, addressing persistence, temporal reasoning, contradiction handling, forgetting, user isolation, and deterministic provenance.

## 1. What the system stores
The system stores structurally decomposed memories as `MemoryRecord` instances. Each memory possesses:
- `user_id` for isolation.
- `subject`, `predicate`, `object` for structured logic.
- `valid_from` and `valid_until` for temporal boundaries.
- `status` (`ACTIVE`, `SUPERSEDED`, `FORGOTTEN`) for explicit lifecycle handling.

## 2. Narrative Ingestion
We begin by ingesting a series of memories spanning time:

1. **Python Era**: Active from Jan 2025 to Jan 2026. Now `SUPERSEDED`.
2. **Java Era**: Active from Jan 2026 to Apr 2026. Now `SUPERSEDED`.
3. **C++ Era**: Active from Apr 2026 onwards. Currently `ACTIVE`.

## 3. Query Demonstrations

### Scenario A: Current Temporal Query
**User:** *"What programming language am I currently using?"*
- **Behavior:** The Query Planner classifies this as a `CURRENT` query. The Reranker enforces a hard filter where `valid_from <= reference_time < valid_until` and `status == ACTIVE`.
- **Retrieval:** `mem_03_cpp`
- **Why a memory was retrieved:** It was semantically relevant AND it is currently valid.

### Scenario B: Historical Temporal Query
**User:** *"What was I using before C++?"*
- **Behavior:** The Query Planner classifies this as a `HISTORICAL` query. The Reranker removes the "currently active" hard filter but continues excluding `FORGOTTEN` memories.
- **Retrieval:** `mem_02_java`
- **Why a memory was updated:** When the user switched to C++, the Java memory was logically updated to `SUPERSEDED` by the Memory Lifecycle engine, preserving it for historical retrieval.

### Scenario C: Timeline Query
**User:** *"How did my language preference change?"*
- **Behavior:** The Query Planner classifies this as a `TIMELINE` query. 
- **Retrieval:** `mem_01_python` ?"> `mem_02_java` ?"> `mem_03_cpp`
- **Why it works:** The Reranker sorts retrieved timeline memories chronologically by `created_at` rather than sorting purely by semantic relevance, preserving the narrative.

### Scenario D: Contradiction Detection
**Ingested Data:** The user says "I like dogs" and later "I like cats". Both are stored as `ACTIVE` because no supersession logic caught the nuance.
**User:** *"What is my favorite animal?"*
- **Behavior:** The system retrieves both active memories. The `ConflictDetector` evaluates them: same subject ("User"), same predicate ("likes"), different objects ("Dog" vs "Cat").
- **Retrieval:** `mem_contra_cat` and `mem_contra_dog`.
- **Flag:** `conflict_detected = True`
- **How contradictions work:** Rather than the LLM silently choosing one or hallucinating, the conflict is explicitly flagged and provided to the LLM so it can answer: *"You have previously stated that you like both cats and dogs..."*

### Scenario E: Forgetting
**Ingested Data:** The user asks to forget their secret code. The lifecycle engine marks `mem_forgotten` as `FORGOTTEN`.
**User:** *"What is my secret code?"*
- **Behavior:** The `FORGOTTEN` status acts as an absolute hard filter in the Reranker.
- **Retrieval:** None.
- **Why a memory is forgotten:** Explicit forgetting is distinct from supersession. A superseded memory is historical; a forgotten memory is inaccessible.

### Scenario F: User Isolation
**Ingested Data:** User 2 creates a highly relevant memory about "ProjectX".
**User 1:** *"What is User 2's project?"*
- **Behavior:** The `RetrievalPipeline` applies a strict `user_id == requested_user_id` hard filter *before* any embeddings or text rankings are evaluated.
- **Retrieval:** None.
- **How privacy works:** User-scoped retrieval happens at the boundary layer. Semantic similarity can never cross the user boundary.

## 4. Provenance
Every memory injected into the LLM context is accompanied by its `memory_id` and the deterministic reasons it survived filtering (e.g., `semantic_match`, `current_state_match`). The LLM cannot fabricate IDs. The final answer relies purely on this verified provenance chain.

