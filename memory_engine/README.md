# Memory Engine Component

This is the **Memory Engine** module for **AnamnesisAI ("The Assistant That Never Forgets... Or Does It?")**, owned by the **Memory Engineer**.

It provides deterministic memory lifecycle management, temporal reasoning, contradiction detection, confidence scoring, half-life decay, and explicit forgetting.

---

## 📁 Architecture

```
memory_engine/
├── __init__.py           # Package exports
├── models.py             # Core Pydantic schemas (Memory, MemoryCandidate, ConflictResult, ResolutionPlan)
├── extractor.py          # Memory extraction (deterministic + pluggable LLM callback)
├── classifier.py         # Memory type, confidence heuristics, and intent detection
├── conflict.py           # Contradiction, duplicate, and temporal conflict detection
├── resolver.py           # State transition engine (active, superseded, forgotten, etc.)
├── temporal.py           # Validity interval reasoning, timeline reconstruction, point-in-time filtering
├── decay.py              # Exponential half-life decay curves and confidence reinforcement
├── engine.py             # MemoryEngine facade API for Backend & Agent engineers
└── tests/
    └── test_memory_engine.py # 10 test suites covering all required hackathon challenge specs
```

---

## 🔌 API Contract for Backend & Agent Engineers

### 1. Data Schema: `Memory`

```json
{
  "id": "mem_a1b2c3d4",
  "user_id": "user_123",
  "subject": "user",
  "predicate": "prefers",
  "object": "C++",
  "memory_type": "preference",
  "confidence": 0.95,
  "status": "active",
  "valid_from": "2026-09-17T12:00:00",
  "valid_until": null,
  "created_at": "2026-09-17T12:00:00",
  "updated_at": "2026-09-17T12:00:00",
  "source_message_id": "msg_456",
  "supersedes": "mem_987xyz",
  "superseded_by": null,
  "provenance_note": "Superseded memory mem_987xyz via message msg_456"
}
```

**Supported Statuses**:
- `active`: Current valid memory
- `superseded`: Replaced by a newer conflicting memory (historical record preserved)
- `expired`: Time-bound memory whose `valid_until` has passed
- `archived`: Stale, decayed memory whose confidence dropped below threshold
- `forgotten`: Explicitly forgotten upon user demand (content redacted/tombstoned)

---

### 2. High-Level Integration Method: `MemoryEngine.process_message`

Use this in FastAPI endpoint when a user sends a message:

```python
from memory_engine import MemoryEngine

plan = MemoryEngine.process_message(
    message="I've switched from Java to C++ for my projects.",
    user_id="user_123",
    message_id="msg_002",
    existing_memories=active_memories_from_db,
    current_time=datetime.utcnow(),
    llm_callable=optional_agent_llm_callback,  # Optional: defaults to built-in deterministic parser
)

# Persist changes to Postgres / pgvector
for new_mem in plan.memories_to_add:
    db.insert_memory(new_mem)

for updated_mem in plan.memories_to_update:
    db.update_memory(updated_mem)
```

---

### 3. Point-in-Time & Historical Timeline Retrieval

Used by Agent/RAG engineer for answering temporal questions:

```python
# "Where do I live now?"
current_location = MemoryEngine.retrieve_memory_state(
    memories=db_memories,
    user_id="user_123",
    predicate="lives_in",
)

# "Where did I live in 2022?"
past_location = MemoryEngine.retrieve_memory_state(
    memories=db_memories,
    user_id="user_123",
    target_time=datetime(2022, 6, 1),
    predicate="lives_in",
)
```

---

### 4. Running the Tests

```bash
python -m pytest memory_engine/tests -v
```
All 10 test scenarios pass:
1. `test_1_new_memory`
2. `test_2_duplicate_memory`
3. `test_3_contradictory_memory`
4. `test_4_temporal_change`
5. `test_5_temporary_information`
6. `test_6_explicit_forgetting`
7. `test_7_confidence_changes`
8. `test_8_multiple_users`
9. `test_9_historical_retrieval`
10. `test_10_unrelated_information`

