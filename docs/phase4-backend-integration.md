# Phase 4 - Backend Contract Integration

## Status
**BACKEND INTEGRATION: PENDING** — The actual backend/PostgreSQL implementation is currently owned by the Backend Engineer and is not yet available.

## AI/Agent Layer Readiness
The AI/Agent branch has fully abstracted the database layer behind the `MemoryRepository` interface (`agent/interfaces.py`). 

The current orchestration relies on:
1. `save()`
2. `get()`
3. `get_all(user_id)`
4. `search(user_id, query_embedding, limit)`

The agent layer currently enforces user isolation via `user_id` filtering, both natively in the `RetrievalPipeline` and explicitly declared in the interface contract.

## Next Steps Upon Backend Availability
Once the PostgreSQL and pgvector backend is delivered, the following actions must be taken:
1. Map the backend's data model to `agent.models.MemoryRecord`.
2. Ensure the backend's semantic search implements Euclidean or Cosine distance securely scoped by the `user_id`.
3. Swap `FakeMemoryRepository` for the real `PostgresMemoryRepository` in the application root/DI container.
4. Execute `agent/tests/eval_harness.py` to prove deterministic temporal constraints and conflict detection still operate correctly over the live database.

