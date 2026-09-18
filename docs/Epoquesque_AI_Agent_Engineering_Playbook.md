# Epoquesque AI/Agent Engineering Playbook

## Autonomous Phase Execution, Validation, Handoffs, and Team Boundaries

**Project:** Epoquesque / AnamnesisAI\
**Role covered by this document:** AI/Agent engineer\
**Primary responsibility:** Memory-aware retrieval, reasoning,
orchestration, provenance, conflict handling, evaluation, and
LLM/embedding provider integration.

------------------------------------------------------------------------

# 1. Mission

Build the AI/Agent layer for Epoquesque without taking ownership of
other engineers' responsibilities.

Epoquesque is a temporal memory engine for an AI assistant.

The core idea is:

> The assistant should not merely remember what the user said. It should
> maintain a versioned model of what is currently true about the user
> while retaining the history needed to explain how it got there.

The AI/Agent engineer owns the intelligence that sits around the
persistence layer:

``` text
User Query
    ↓
Query Planning
    ↓
Embedding
    ↓
Memory Retrieval
    ↓
Hard Filtering
    ↓
Temporal Reasoning
    ↓
Reranking
    ↓
Conflict Detection
    ↓
Context Construction
    ↓
LLM Generation
    ↓
Deterministic Provenance
    ↓
AgentResponse
```

The persistence implementation is owned by the backend/database
engineer.

------------------------------------------------------------------------

# 2. NON-NEGOTIABLE TEAM BOUNDARIES

## 2.1 Backend/database engineer owns

Do NOT take over or rewrite:

-   PostgreSQL setup
-   pgvector setup
-   database schema implementation
-   migrations
-   database connection management
-   FastAPI application structure
-   backend authentication
-   backend user/session authorization
-   backend CRUD endpoints
-   database deployment
-   production database configuration

The AI/Agent engineer may define an interface/contract that the backend
implementation must satisfy.

The AI/Agent engineer may provide:

-   repository interface requirements
-   expected query semantics
-   required fields
-   expected retrieval inputs/outputs
-   integration contract
-   tests against a fake repository

Do not implement the backend engineer's concrete database solution.

------------------------------------------------------------------------

## 2.2 Frontend engineer owns

Do NOT take over:

-   React application
-   UI pages
-   styling system
-   frontend routing
-   frontend authentication screens
-   memory visualization UI
-   frontend API client

The AI/Agent engineer may provide the frontend with the final
response/provenance contract.

------------------------------------------------------------------------

## 2.3 Memory engineer owns

Do NOT independently redesign:

-   memory extraction
-   memory creation policy
-   memory lifecycle policy
-   memory update policy
-   memory deletion/forgetting policy
-   contradiction resolution at ingestion time
-   memory persistence semantics

The AI/Agent layer consumes MemoryRecords according to the agreed
contract.

If an AI/Agent requirement reveals a missing memory-engine capability:

1.  document the requirement;
2.  do not silently redesign the memory engine;
3.  create an integration note;
4.  coordinate through the agreed interface/branch.

------------------------------------------------------------------------

## 2.4 AI/Agent engineer owns

This branch may own:

-   QueryPlanner integration
-   retrieval orchestration
-   reranking
-   temporal query interpretation
-   context construction
-   LLM provider abstraction
-   embedding provider abstraction
-   concrete LLM provider integration when approved
-   concrete embedding provider integration when approved
-   conflict detection at answer/retrieval time
-   provenance generation
-   uncertainty handling
-   retrieval evaluation
-   agent orchestration
-   agent-specific tests
-   deterministic fake implementations
-   integration adapters that do not alter backend ownership

------------------------------------------------------------------------

# 3. SOURCE OF TRUTH RULE

Never trust an old agent report, previous conversation, task summary, or
implementation plan over the actual workspace.

At the beginning of EVERY phase:

``` bash
git status
git branch --show-current
git log --oneline --decorate --graph -15
git diff
git diff --cached
```

Then inspect the actual files.

If a previous agent claims something exists, verify it.

If a previous agent claims tests pass, run them.

If a previous agent claims a component is complete, inspect the
implementation.

------------------------------------------------------------------------

# 4. GIT SAFETY

The AI/Agent engineer must:

-   work only on the assigned branch;
-   never push to `main`;
-   never force-push;
-   never reset another engineer's branch;
-   never overwrite another engineer's work;
-   never modify another engineer's implementation merely to make tests
    pass;
-   never commit automatically unless explicitly requested;
-   never push automatically unless explicitly requested.

Before modifying shared interfaces:

1.  inspect current interface;
2.  determine whether the change is necessary;
3.  document the compatibility impact;
4.  prefer additive changes;
5.  do not break existing contracts without coordination.

Never use:

``` bash
git push --force
git reset --hard
git clean -fd
```

unless explicitly instructed by the user.

------------------------------------------------------------------------

# 5. ENGINEERING LOOP

Every phase follows this loop automatically.

``` text
INSPECT
  ↓
UNDERSTAND
  ↓
PLAN
  ↓
IMPLEMENT
  ↓
UNIT TEST
  ↓
EDGE-CASE TEST
  ↓
INTEGRATION TEST
  ↓
STATIC ANALYSIS
  ↓
SECURITY REVIEW
  ↓
FAILURE ANALYSIS
  ↓
FIX
  ↓
RE-RUN ALL REGRESSION TESTS
  ↓
DIFF REVIEW
  ↓
DOCUMENT
  ↓
PHASE AUDIT
  ↓
ONLY THEN ADVANCE
```

Do not stop because the first test run passes.

After every meaningful implementation change:

``` text
run targeted tests
→ run complete agent tests
→ run mypy
→ run flake8
→ inspect diff
```

Before declaring a phase complete:

``` text
full tests
+ regression tests
+ boundary tests
+ security tests
+ integration contract tests
+ static analysis
+ import verification
+ git hygiene
+ documentation
```

------------------------------------------------------------------------

# 6. FAILURE POLICY

If a test fails:

1.  reproduce it;
2.  identify the actual root cause;
3.  determine whether the bug belongs to this branch;
4.  fix the root cause;
5.  add/regain a regression test;
6.  run the affected tests;
7.  run the complete suite;
8.  run static analysis again.

Do NOT:

-   weaken the test;
-   delete the test;
-   loosen requirements merely to get green;
-   hardcode the expected answer;
-   bypass a failing component;
-   blame another branch without evidence.

If the problem belongs to another engineer:

-   do not modify their implementation;
-   document the exact contract problem;
-   create a minimal adapter if appropriate;
-   report the required change.

------------------------------------------------------------------------

# 7. PHASE GATES

A phase cannot advance unless its gate passes.

## Gate A --- Functional correctness

All required behavior works.

## Gate B --- Regression safety

All previous tests still pass.

## Gate C --- Type/lint correctness

``` bash
mypy agent
flake8 agent
```

must pass.

## Gate D --- Determinism

Tests must not depend on:

-   current wall-clock time;
-   network;
-   API availability;
-   database state;
-   random embeddings;
-   random model output.

## Gate E --- Security

Verify:

-   user isolation;
-   forgotten-memory exclusion;
-   provenance integrity;
-   prompt-injection handling;
-   no secret leakage.

## Gate F --- Contract correctness

Interfaces must remain compatible with other engineers' work.

## Gate G --- Git hygiene

No:

``` text
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.env
*.db
credentials
API keys
```

## Gate H --- Documentation

Every completed phase must have a concise technical document.

------------------------------------------------------------------------

# 8. PHASE 1 --- FOUNDATION

## Status

Already completed.

Verified foundation includes:

-   MemoryRecord
-   QueryPlan
-   RankingConfig
-   Reranker
-   ContextBuilder
-   ProvenanceManager
-   provider abstractions
-   fake providers
-   deterministic tests
-   temporal validation
-   confidence bounds
-   strict query planning
-   git hygiene

Phase 1 verification reported:

-   61 tests
-   mypy clean
-   flake8 clean
-   import verification successful

Do NOT redo Phase 1 unless a later integration test demonstrates a
genuine Phase 1 defect.

Reference:

``` text
docs/phase1-code-review.md
```

------------------------------------------------------------------------

# 9. PHASE 2A --- RETRIEVAL ENGINE + AGENT ORCHESTRATION

## Objective

Connect the Phase 1 components into a complete deterministic agent
pipeline without PostgreSQL, Gemini, FastAPI, or frontend integration.

Target:

``` text
Agent.run()
    ↓
QueryPlanner
    ↓
EmbeddingProvider
    ↓
MemoryRepository.search()
    ↓
Hard Filters
    ↓
Reranker
    ↓
ConflictDetector
    ↓
ProvenanceManager
    ↓
ContextBuilder
    ↓
LLMProvider
    ↓
AgentResponse
```

## Required behavior

### Current queries

Must use current temporal validity:

``` text
status == ACTIVE
AND
valid_from <= reference_time
AND
(
    valid_until is null
    OR
    reference_time < valid_until
)
```

`valid_from` is inclusive.

`valid_until` is exclusive.

### Historical queries

May retrieve superseded/expired memories when historically relevant.

### Timeline queries

May retrieve multiple historical states and must preserve chronological
meaning.

### Forgotten memories

Must never be authoritative retrieval sources.

### User isolation

A memory belonging to another user must never reach:

-   reranking;
-   context;
-   provenance;
-   LLM.

### Provenance

Must be generated from actual retrieved records.

### Conflict detection

Contradictory active/current memories must produce an explicit conflict
state instead of silently selecting one.

------------------------------------------------------------------------

# 10. PHASE 2A AUDIT REQUIREMENTS

Before advancing, independently test:

## Temporal

-   exact valid_from;
-   exact valid_until;
-   immediately before boundary;
-   immediately after boundary;
-   no valid_from;
-   no valid_until;
-   future memory;
-   expired memory;
-   timezone-aware timestamps.

## Retrieval

-   semantic match;
-   irrelevant query;
-   multiple candidates;
-   duplicate candidates;
-   historical retrieval;
-   timeline retrieval;
-   current retrieval.

## Security

-   cross-user high-similarity memory;
-   forgotten high-similarity memory;
-   prompt injection in memory;
-   fake provenance attempt;
-   duplicate provenance.

## Ranking

-   semantic score;
-   confidence;
-   temporal relevance;
-   recency;
-   configurable weights;
-   hard-filter precedence.

## Conflict

-   two active contradictory memories;
-   superseded + active memory;
-   same object repeated;
-   irrelevant conflicting memories;
-   expired conflicting memories.

## No-memory behavior

The agent must not invent a remembered fact.

------------------------------------------------------------------------

# 11. RELEVANCE THRESHOLD POLICY

Do not introduce arbitrary thresholds without evidence.

If a relevance threshold exists:

-   make its location explicit;
-   make it configurable;
-   test its effect;
-   test different query types;
-   verify historical memories are not incorrectly discarded;
-   verify irrelevant memories do not survive.

A threshold must not replace hard constraints.

Hard filtering always occurs first.

------------------------------------------------------------------------

# 12. PHASE 2A COMPLETION GATE

Before moving forward:

``` bash
python -m pytest agent/tests/ -v
mypy agent
flake8 agent
```

Also run:

-   import verification;
-   retrieval evaluation;
-   security regression tests;
-   git hygiene check.

Create:

``` text
docs/phase2-code-review.md
```

Only proceed if the audit finds no unresolved BLOCKER.

------------------------------------------------------------------------

# 13. PHASE 2B --- RETRIEVAL EVALUATION

This phase focuses on proving retrieval quality without changing the
backend.

Build a deterministic evaluation suite.

## Evaluation dimensions

### Current-state accuracy

Given a sequence:

``` text
Python → Java → C++
```

current query must retrieve C++.

### Historical accuracy

"before C++" should retrieve the relevant predecessor.

### Timeline accuracy

A timeline query should produce:

``` text
Python → Java → C++
```

not semantic-score order.

### Isolation accuracy

User A must never retrieve User B's memory.

### Lifecycle accuracy

Forgotten memories must not become sources.

### Conflict accuracy

Unresolved active contradictions must be surfaced.

## Evaluation output

Every evaluation should report:

``` text
case
query
reference_time
expected_memory_ids
actual_memory_ids
pass/fail
reason
```

Do not rely only on generated natural-language answers.

------------------------------------------------------------------------

# 14. PHASE 3 --- REAL LLM + EMBEDDING PROVIDERS

Only begin this phase after the retrieval audit is clean.

## Objective

Replace deterministic providers with real provider implementations while
keeping the core agent provider-agnostic.

Architecture:

``` text
LLMProvider
    ↑
GeminiLLMProvider

EmbeddingProvider
    ↑
ConcreteEmbeddingProvider
```

The domain logic must depend on interfaces, not SDK-specific classes.

## Rules

Do NOT import Gemini SDK code into:

-   models.py
-   reranker.py
-   retrieval.py
-   orchestrator.py
-   query_planner.py

Provider-specific code belongs under:

``` text
agent/providers/
```

## Provider requirements

### LLM provider

Must:

-   accept structured context;
-   return text;
-   handle provider errors;
-   avoid exposing secrets;
-   remain replaceable;
-   be testable through the existing fake provider.

### Embedding provider

Must:

-   produce deterministic vector shape;
-   document dimensionality;
-   handle API failures;
-   remain replaceable;
-   preserve the same interface as the fake provider.

## Never expose API keys

Use environment configuration.

Never commit:

``` text
.env
credentials
service-account keys
API keys
```

------------------------------------------------------------------------

# 15. PHASE 3 VALIDATION

Use a two-layer strategy.

## Offline regression suite

All previous tests must continue passing without network.

## Provider integration tests

Only when credentials are available:

-   test one real embedding request;
-   test one real LLM request;
-   verify response parsing;
-   verify failure handling.

Real-provider tests must be isolated so the normal test suite does not
require credentials.

For example:

``` text
agent/tests/
    unit/
    integration/
```

Integration tests should be explicitly opt-in.

Never make CI/unit testing dependent on an external API.

------------------------------------------------------------------------

# 16. PHASE 4 --- BACKEND INTEGRATION CONTRACT

The backend engineer owns PostgreSQL/pgvector.

The AI/Agent engineer must NOT implement their database.

Instead, define and validate the integration contract.

Expected conceptual repository behavior:

``` text
search(
    user_id,
    query_embedding,
    limit,
    filters
)
```

The exact signature must be negotiated against the backend
implementation.

## Required semantics

The real repository must support:

-   user-scoped search;
-   semantic candidate retrieval;
-   lifecycle/status filtering;
-   temporal metadata;
-   enough information for reranking;
-   historical retrieval;
-   timeline retrieval.

## Integration process

1.  Inspect backend engineer's repository/API implementation.
2.  Compare it against the AI/Agent interface.
3.  Identify mismatches.
4.  Prefer a small adapter when appropriate.
5.  Do not rewrite their database implementation.
6.  Add contract/integration tests on the AI/Agent side.
7.  Validate end-to-end retrieval.

If a backend change is genuinely required:

``` text
document requirement
→ notify backend engineer
→ coordinate interface
→ test compatibility
```

Do not silently modify their code.

------------------------------------------------------------------------

# 17. PHASE 4 VALIDATION

Test with realistic persisted memories:

``` text
Python
→ superseded

Java
→ superseded

C++
→ active
```

Test:

``` text
current query
historical query
timeline query
conflict
forgetting
user isolation
duplicate retrieval
irrelevant query
```

Compare:

``` text
FakeMemoryRepository
vs
RealMemoryRepository
```

The same agent behavior should hold.

------------------------------------------------------------------------

# 18. PHASE 5 --- END-TO-END AGENT HARDENING

Once real providers and backend integration work, harden the agent.

## Reliability

Handle:

-   empty retrieval;
-   provider timeout;
-   provider error;
-   malformed provider response;
-   embedding failure;
-   repository failure;
-   context overflow;
-   duplicate memories;
-   conflicting memories;
-   stale memories.

## Uncertainty

The agent should distinguish:

``` text
No evidence
Weak evidence
Strong evidence
Conflict
```

Do not turn uncertainty into confident hallucination.

## Provenance

Every factual memory-grounded answer should have deterministic source
metadata.

The LLM does not become the source-of-truth for provenance.

------------------------------------------------------------------------

# 19. PHASE 5 VALIDATION MATRIX

Run all of:

### Functional

-   current;
-   historical;
-   timeline;
-   general;
-   ambiguous.

### Memory lifecycle

-   active;
-   superseded;
-   forgotten;
-   expired;
-   future.

### Security

-   cross-user;
-   prompt injection;
-   provenance integrity;
-   secret leakage.

### Reliability

-   empty DB;
-   provider unavailable;
-   malformed response;
-   duplicate results;
-   conflicting results.

### Regression

All previous tests.

------------------------------------------------------------------------

# 20. PHASE 6 --- DEMO / HACKATHON SCENARIO VALIDATION

The final demo should prove the actual differentiator.

## Scenario

### Day 1

User:

> I'm learning Python.

Memory:

``` text
Python
ACTIVE
```

### Day 20

User:

> I switched to Java.

Memory state:

``` text
Python → SUPERSEDED
Java → ACTIVE
```

### Day 60

User:

> I'm using C++ now.

Memory state:

``` text
Python → SUPERSEDED
Java → SUPERSEDED
C++ → ACTIVE
```

## Current query

``` text
What programming language am I currently using?
```

Expected:

``` text
C++
```

Provenance should identify the C++ memory.

## Historical query

``` text
What was I using before C++?
```

Expected:

``` text
Java
```

## Timeline query

``` text
How did my programming language preference change?
```

Expected temporal sequence:

``` text
Python → Java → C++
```

## Conflict demo

Create two unresolved active contradictory memories.

Expected:

``` text
conflict_detected = true
```

The system must not silently select one.

## Forgetting demo

Explicitly mark a memory forgotten.

Verify:

-   it is not retrieved as an authoritative memory;
-   it does not appear in provenance;
-   it does not leak into the answer.

------------------------------------------------------------------------

# 21. AUTOMATED SELF-VALIDATION

The agent must continuously validate itself.

After each implementation phase:

## Level 1 --- Unit

Test the changed component.

## Level 2 --- Package

Run:

``` bash
python -m pytest agent/tests/ -v
```

## Level 3 --- Static

Run:

``` bash
mypy agent
flake8 agent
```

## Level 4 --- Integration

Run all available fake/integration contract tests.

## Level 5 --- Adversarial

Test:

-   wrong user;
-   forgotten memory;
-   future memory;
-   expired memory;
-   contradictory memory;
-   prompt injection;
-   duplicate source;
-   empty memory;
-   provider failure.

## Level 6 --- Regression

Run the entire test suite again after fixes.

## Level 7 --- Diff

Inspect:

``` bash
git diff
git diff --stat
git status
```

## Level 8 --- Documentation

Update the phase document.

Only after all eight levels pass may the phase be declared complete.

------------------------------------------------------------------------

# 22. AUTOMATIC RETRY POLICY

If any validation fails:

``` text
FAIL
 ↓
Diagnose
 ↓
Fix
 ↓
Targeted test
 ↓
Full suite
 ↓
Static analysis
 ↓
Security tests
 ↓
Diff review
```

Repeat until:

``` text
all required gates PASS
```

Do not ask the user whether to fix an obvious defect.

Do not stop after one failed attempt.

If a failure is genuinely blocked by another engineer's unfinished
dependency, stop only that dependency and continue all work that can be
validated independently.

Document:

``` text
BLOCKED BY:
EXPECTED CONTRACT:
CURRENT WORKAROUND:
FILES NOT MODIFIED:
NEXT REQUIRED HANDOFF:
```

------------------------------------------------------------------------

# 23. HANDOFF PROTOCOL

At the end of every phase produce a machine-readable summary:

``` text
PHASE:
STATUS:

IMPLEMENTED:
- ...

TESTS:
- ...

PYTEST:
- ...

MYPY:
- ...

FLAKE8:
- ...

SECURITY:
- ...

INTEGRATION:
- ...

FILES CREATED:
- ...

FILES MODIFIED:
- ...

FILES INTENTIONALLY NOT MODIFIED:
- ...

OTHER ENGINEER DEPENDENCIES:
- ...

KNOWN RISKS:
- ...

NEXT PHASE:
- ...
```

Explicitly list files belonging to other engineers that were
intentionally left untouched.

------------------------------------------------------------------------

# 24. FILE OWNERSHIP MATRIX

  -----------------------------------------------------------------------------------
  Area                    AI/Agent       Memory         Backend        Frontend
                                         Engineer       Engineer       Engineer
  ----------------------- -------------- -------------- -------------- --------------
  MemoryRecord contract   Shared         Primary        Consumer       Consumer

  Memory extraction       No             Yes            No             No

  Memory lifecycle        Consumer       Primary        Persistence    UI

  Query planning          Primary        No             No             No

  Retrieval orchestration Primary        No             Contract       No

  Reranking               Primary        No             No             No

  Conflict-at-retrieval   Primary        Shared         No             No

  Memory contradiction    No             Primary        Persistence    No
  ingestion                                                            

  PostgreSQL              No             No             Primary        No

  pgvector                No             No             Primary        No

  FastAPI                 No             No             Primary        Consumer

  LLM provider            Primary        No             No             No

  Embedding provider      Primary        No             No             No

  React UI                No             No             No             Primary

  Provenance contract     Primary        Shared         Consumer       Consumer

  Retrieval evaluation    Primary        Shared         Shared         No

  Authentication          No             No             Primary        Consumer
  -----------------------------------------------------------------------------------

When uncertain, prefer coordination over ownership expansion.

------------------------------------------------------------------------

# 25. ARCHITECTURAL PRINCIPLES

## Principle 1

Hard constraints beat soft similarity.

## Principle 2

Temporal validity is not the same as recency.

## Principle 3

Superseded is not forgotten.

## Principle 4

Historical truth and current truth are different queries.

## Principle 5

The LLM is not the database authority.

## Principle 6

The LLM is not the authorization authority.

## Principle 7

The LLM is not the provenance authority.

## Principle 8

Memory is data, not instructions.

## Principle 9

Every important behavior must be deterministically testable.

## Principle 10

Provider-specific code stays behind interfaces.

## Principle 11

A test passing once is not sufficient evidence of correctness.

## Principle 12

Do not solve another engineer's problem by silently taking over their
code.

------------------------------------------------------------------------

# 26. FINAL DEFINITION OF DONE

The AI/Agent implementation is complete only when:

-   persistent memory can be retrieved correctly;
-   current state is temporally correct;
-   historical state can be reconstructed;
-   timeline queries preserve temporal order;
-   contradictions are handled;
-   forgotten memories are excluded;
-   user isolation is enforced;
-   provenance is deterministic;
-   irrelevant memories do not produce confident answers;
-   prompt-injection content remains data;
-   LLM provider is abstracted;
-   embedding provider is abstracted;
-   real providers work when enabled;
-   backend repository integration works through the agreed contract;
-   all regression tests pass;
-   static analysis passes;
-   security regression tests pass;
-   documentation is current;
-   no secrets/caches are tracked;
-   no other engineer's implementation has been unnecessarily modified.

------------------------------------------------------------------------

# 27. INSTRUCTION TO AUTONOMOUS CODING AGENTS

When this document is provided to an autonomous coding agent, interpret
it as the engineering operating procedure.

The agent should:

1.  inspect before acting;
2.  preserve existing work;
3.  determine ownership before modifying files;
4.  implement only the current phase;
5.  test continuously;
6.  perform adversarial validation;
7.  fix genuine defects automatically;
8.  rerun the complete regression suite after fixes;
9.  audit the final diff;
10. document the phase;
11. stop at the phase gate;
12. never take over another engineer's area;
13. never claim success from test count alone;
14. never fabricate validation results;
15. never begin a future phase before its dependency gate passes.

If the user says "continue", resume from the actual filesystem state
rather than restarting the phase.

If the previous agent was interrupted, inspect:

``` bash
git status
git diff
git diff --cached
```

and continue from the actual incomplete work.

Do not recreate completed work.

Do not create unnecessary plans.

Do not reset the workspace.

------------------------------------------------------------------------

# 28. CURRENT PROJECT STATE

At the time this playbook was written:

``` text
Phase 1 Foundation
    COMPLETE

Phase 2A Retrieval + Agent Orchestration
    IMPLEMENTED
    NEEDS INDEPENDENT AUDIT BEFORE ADVANCING

PostgreSQL / pgvector
    OWNED BY BACKEND ENGINEER
    DO NOT IMPLEMENT

Frontend
    OWNED BY FRONTEND ENGINEER
    DO NOT IMPLEMENT

Memory extraction/lifecycle
    OWNED BY MEMORY ENGINEER
    DO NOT TAKE OVER

Real LLM / Embedding integration
    NEXT AI/AGENT OWNED PHASE AFTER 2A AUDIT
```

The immediate next action is:

``` text
INDEPENDENT PHASE 2A AUDIT
        ↓
FIX ONLY AI/AGENT DEFECTS
        ↓
FULL REGRESSION
        ↓
PHASE 2A GATE
        ↓
REAL PROVIDER INTEGRATION
```

------------------------------------------------------------------------

# 29. DO NOT CONFUSE INFRASTRUCTURE WITH INTELLIGENCE

The project should preserve this separation:

``` text
                EPOQUESQUE
                    │
       ┌────────────┴────────────┐
       │                         │
 MEMORY / DATABASE          AI / AGENT
       │                         │
 PostgreSQL                  Retrieval
 pgvector                    Reranking
 Persistence                 Temporal reasoning
 Memory lifecycle            Conflict detection
 User storage               Context
                             LLM
                             Provenance
       │                         │
       └────────────┬────────────┘
                    │
              Final Assistant
```

The AI/Agent branch should consume persistence capabilities through
contracts rather than implementing the persistence system itself.

This allows both engineers to work in parallel without blocking each
other.

------------------------------------------------------------------------

# 30. FINAL RULE

The goal is not to produce the largest codebase.

The goal is to produce a system where every important claim can be
demonstrated:

``` text
"This memory was selected"
        ↓
"because it was semantically relevant"
        ↓
"and valid at this point in time"
        ↓
"and belonged to this user"
        ↓
"and was not forgotten"
        ↓
"and survived hard filtering"
        ↓
"and ranked appropriately"
        ↓
"and was actually supplied to the LLM"
        ↓
"and the final answer can show exactly why."
```

That chain is the core technical identity of Epoquesque.
