# Phase 2B Retrieval Evaluation Report

Generated at: 2026-09-18T11:34:38.855292

## Evaluation Cases

### 1. Current-state retrieval
- **Query**: `What programming language am I currently using?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `['mem_03_cpp']`
- **Actual IDs**: `['mem_03_cpp']`
- **Result**: `PASS`
- **Reason**: All assertions passed.

### 2. Historical retrieval
- **Query**: `What was I using before C++?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `['mem_02_java']`
- **Actual IDs**: `['mem_02_java']`
- **Result**: `PASS`
- **Reason**: All assertions passed.

### 3. Timeline retrieval (Order verified implicitly by ID array match)
- **Query**: `How did my language preference change?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `['mem_01_python', 'mem_02_java', 'mem_03_cpp']`
- **Actual IDs**: `['mem_01_python', 'mem_02_java', 'mem_03_cpp']`
- **Result**: `PASS`
- **Reason**: All assertions passed.

### 4. Contradiction handling
- **Query**: `What is my favorite animal?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `['mem_contra_cat', 'mem_contra_dog']`
- **Actual IDs**: `['mem_contra_cat', 'mem_contra_dog']`
- **Result**: `PASS`
- **Reason**: All assertions passed.

### 5. Forgotten-memory exclusion
- **Query**: `What is my secret code?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `[]`
- **Actual IDs**: `[]`
- **Result**: `PASS`
- **Reason**: All assertions passed.

### 6. User isolation
- **Query**: `What is the user's project?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `[]`
- **Actual IDs**: `[]`
- **Result**: `PASS`
- **Reason**: All assertions passed.

### 7. Irrelevant-query rejection
- **Query**: `What color is the sky?`
- **Reference Time**: `2026-09-18T10:00:00`
- **Expected IDs**: `[]`
- **Actual IDs**: `[]`
- **Result**: `PASS`
- **Reason**: All assertions passed.

