# Phase 2A: Retrieval Engine & Agent Orchestration

## Overview
Phase 2A introduces the core retrieval pipeline and agent orchestration layer, linking the query planner and context builder developed in Phase 1 with a deterministic test harness.

The system is designed to work entirely in-memory using deterministic fake providers (LLM, Embeddings, MemoryRepository) to strictly enforce constraints and guarantee testability prior to any network integration.

## Pipeline Architecture
The `Agent.run()` method executes the following steps:

1. **Query Planning**: `DeterministicQueryPlanner` maps the input query to a `QueryPlan` (`CURRENT`, `HISTORICAL`, `TIMELINE`, etc.).
2. **Candidate Retrieval**: `RetrievalPipeline.retrieve()` fetches user-scoped candidates from the `MemoryRepository` using semantic search.
3. **Filtering & Ranking**: `Reranker.rerank()` applies hard filters (dropping forgotten or temporally invalid memories depending on query type) and ranks candidates using a configurable weighted scoring system (semantic similarity, confidence, temporal validity, and recency).
4. **Irrelevance Pruning**: The pipeline drops any returned memories whose total score falls below the relevance threshold (`>= 0.55`).
5. **Conflict Detection**: `ConflictDetector` evaluates active, current memories to identify contradictions.
6. **Provenance Generation**: `ProvenanceManager` logs the exact memory IDs injected into the context, along with specific reasons and deduplicates overlapping candidates.
7. **Context Construction**: `ContextBuilder` wraps the instructions, user query, and raw memory context into a strictly delineated LLM prompt.
8. **Generation**: The `LLMProvider` generates an answer based strictly on the retrieved context.

## Hard and Soft Filtering
* **Hard Filters**: Enforced via list comprehension in the `Reranker`. `FORGOTTEN` memories are always dropped. For `CURRENT` queries, expired or superseded memories are dropped. `HISTORICAL` and `TIMELINE` queries bypass the `CURRENT` filter, permitting superseded memories.
* **Soft Ranking**: Combines Semantic Similarity (40%), Confidence (20%), Temporal Validity (20%), and Recency (20%). For `TIMELINE` queries, the results are ultimately re-sorted chronologically to preserve narrative flow.

## Conflict Detection
The `ConflictDetector` examines the final, top-k candidate set for memories that are both `ACTIVE` and `CURRENT`. It raises a `conflict_detected` flag if multiple memories share the exact same `subject` and `predicate` but possess different `object` values.

## Evaluation Harness
`agent/tests/eval_harness.py` provides an end-to-end testing utility verifying temporal traversal, semantic filtering, and orchestration.

