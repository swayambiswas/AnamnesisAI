# AnamnesisAI Frontend Design & Engineering Playbook

## 1. Mission

Build a premium, cinematic, highly polished frontend for **AnamnesisAI**, a temporal memory engine for AI assistants.

Core product idea:

> **An AI that remembers what changed.**

The frontend is not merely a chat UI. It must make the project's technical differentiator visible:

- persistent memory
- temporal truth
- memory evolution
- contradiction handling
- explicit forgetting
- user-private memory
- memory provenance
- confidence and lifecycle
- explainable retrieval

The website should feel like a serious AI product/demo suitable for a technical hackathon judging panel.

## 2. Read These Files First

Before changing or creating frontend code, read:

1. `docs/Epoquesque_AI_Agent_Engineering_Playbook.md`
2. This file: `docs/Epoquesque_Frontend_Design_Playbook.md`

The AI/Agent playbook is the source of truth for the existing intelligence layer.

The frontend playbook is the source of truth for visual language and frontend architecture.

Do not redesign or rewrite the AI/Agent architecture.

## 3. Ownership Boundaries

### Frontend owns

- React/Vite application
- visual design
- responsive layout
- animations
- navigation
- chat presentation
- memory visualization
- timeline visualization
- conflict visualization
- provenance presentation
- frontend state
- mock API adapter
- frontend components and styling

### AI/Agent engineer owns

- retrieval
- query planning
- ranking
- temporal filtering
- conflict detection
- provenance generation
- LLM orchestration
- embeddings
- AI-side interfaces

### Backend engineer owns

- FastAPI
- PostgreSQL
- pgvector
- authentication
- persistence
- database schema
- backend API implementation

### Critical rule

The frontend must NOT implement PostgreSQL, pgvector, FastAPI, authentication infrastructure, or duplicate the AI/Agent logic.

The backend is currently under development. That is expected and is NOT a blocker for frontend work.

Build against a stable frontend mock API contract so the real backend can be connected later.

# 4. Product Identity

## Name

**ANAMNESIS**

Supporting descriptor:

**Temporal memory for AI assistants.**

Use the full name **AnamnesisAI** where technical/product clarity is useful.

## Brand idea

Anamnesis means recollection/memory.

The visual identity should communicate:

- memory
- time
- persistence
- evolution
- fragments becoming a coherent history
- present state emerging from past states

Avoid literal "brain" imagery, generic robot imagery, or cheesy neural-network graphics.

# 5. Visual Direction

The desired aesthetic is:

**premium AI product × editorial website × cinematic motion**

Use inspiration from modern design-system-driven websites and premium editorial/motorsport presentation:

- oversized typography
- strong contrast
- large visual moments
- asymmetric layouts
- deliberate whitespace
- sharp section transitions
- cinematic movement
- confident typography
- subtle technical details

The Lando Norris website is inspiration for energy, editorial composition, motion and visual confidence — NOT something to copy.

Do not reproduce another site's exact layout, branding, assets, or distinctive components.

Anamnesis must remain recognizably an AI/memory product.

# 6. Color System

Prefer a restrained dark-first palette.

Base:

- near-black background
- charcoal / graphite surfaces
- off-white primary text
- muted gray secondary text

Accent:

Use ONE primary accent family consistently.

Recommended direction:

- electric lime / acid green OR
- warm amber / yellow

Do not turn the entire interface into neon.

Use the accent for:

- active states
- memory connections
- important metadata
- timeline events
- CTA emphasis
- provenance indicators
- small visual highlights

Use opacity and neutral tones heavily so the accent remains meaningful.

All colors must be defined as design tokens.

Do not scatter arbitrary hex values throughout components.

# 7. Typography

Use a modern sans-serif with strong display capability.

Preferred approach:

- bold/black display face for hero headings
- clean sans-serif for UI/body
- monospace for technical metadata

Typography hierarchy must be obvious.

Hero:

Very large responsive typography.

Example:

ANAMNESIS

An AI that
remembers what
changed.

Body:

Readable and restrained.

Technical metadata:

Use monospace for:

- memory IDs
- timestamps
- confidence
- status
- retrieval reasons
- API/debug information

Do not overuse monospace.

# 8. Design Tokens

Create a central token system for:

- colors
- typography sizes
- spacing
- border radius
- shadows
- transition durations
- easing curves
- z-index layers

Components should consume tokens rather than inventing their own values.

If a visual value needs to change globally, it should be possible to modify the token system.

Avoid dozens of unrelated rounded-card styles.

Use a coherent radius language.

# 9. Motion Philosophy

Motion is a major part of the identity.

However:

> Motion must communicate meaning, not merely decoration.

Use:

- scroll-triggered reveals
- staggered text entrances
- spring transitions
- subtle parallax
- timeline movement
- card expansion
- state transitions
- page transitions
- hover micro-interactions

Do NOT use:

- excessive bouncing
- constant floating elements
- random particle effects everywhere
- distracting infinite animations
- slow animations that make the UI feel sluggish

## Memory-specific motion

The strongest animations should represent memory lifecycle.

### Active memory

Moves into the foreground.

### Superseded memory

Transitions backward into history.

### Forgotten memory

Fades/dissolves from the active memory layer.

### Contradiction

Two memory states should visibly coexist before the system explains the conflict.

### Timeline

Memory events should appear sequentially as the user explores history.

These animations should make the system understandable even before a presenter explains it.

# 10. Landing Page

Create a polished long-form landing page.

## Hero

Large statement:

> ANAMNESIS

> An AI that remembers what changed.

Supporting text:

> A temporal memory engine that maintains what is currently true, preserves what used to be true, and explains why.

Primary CTA:

**Enter the Memory**

Secondary CTA:

**Explore the System**

Hero visual:

A dynamic layered memory timeline / fragments converging toward a current state.

Avoid generic AI chatbot screenshots as the hero.

## Section: The Problem

Heading:

> Vector similarity isn't memory.

Explain visually:

A conventional RAG system can retrieve semantically similar memories without understanding whether they are:

- current
- historical
- superseded
- forgotten
- contradictory

Show two similar memory cards with different temporal states.

## Section: Memory Evolves

Show:

```text
Python
   ↓
Java
   ↓
C++
 CURRENT
```

The old states remain visible as history.

Emphasize:

> Current truth ≠ latest retrieved sentence.

## Section: Contradictions

Interactive visualization:

```text
CAT
 │
 ├── contradiction
 │
DOG
```

Then show temporal/context information used by the agent.

Do not simply label one memory "correct" without showing the evidence/state.

## Section: Forgetting

Demonstrate the difference between:

- no longer true
- explicitly forgotten

Example:

```text
Superseded
→ remains in history

Forgotten
→ excluded from retrieval
```

## Section: Provenance

Show:

> Every answer can explain which memories informed it.

Example:

```text
WHY THIS ANSWER?

mem_03_cpp
Current state
94% confidence

mem_02_java
Historical context
91% confidence
Superseded
```

## Section: Multi-user Privacy

Show isolated memory spaces.

Example:

```text
USER A
├── memories
├── conversations
└── timeline

USER B
├── memories
├── conversations
└── timeline
```

Never imply one user's memories can leak into another user's context.

## Final CTA

> Give your assistant a memory.

Button:

**Enter Anamnesis**

# 11. Assistant Application

The main interactive product should have a dedicated assistant experience.

Recommended layout:

```text
┌─────────────────────────────────────────────────────────────┐
│ ANAMNESIS                                  Memory / Profile │
├───────────────────┬─────────────────────────┬───────────────┤
│                   │                         │               │
│ Conversations     │       Chat              │ Memory        │
│                   │                         │ Context       │
│ Today             │                         │               │
│ Yesterday         │                         │ mem_03_cpp     │
│ Earlier           │                         │ ACTIVE         │
│                   │                         │ 94% confidence │
│ Timeline          │                         │               │
│ Memories          │                         │ Why? →         │
│                   │                         │               │
└───────────────────┴─────────────────────────┴───────────────┘
```

On smaller screens, collapse the side panels into drawers/sheets.

# 12. Chat UI

The chat must look premium but remain usable.

User message:

Minimal.

Assistant message:

More structured.

Assistant response should support:

- answer
- confidence/uncertainty
- source memories
- conflict indicator
- "Why this answer?"
- relevant timeline

Example:

```text
You're currently using C++.

────────────────────────
MEMORY CONTEXT

mem_03_cpp
Current preference
94% confidence

Why this memory?
Current-state match
Semantic match
Active memory
```

The frontend should not fabricate these reasons.

Render whatever provenance the backend/agent provides.

# 13. Memory Panel

Create a reusable `MemoryCard`.

Fields:

- memory ID
- subject
- predicate
- object
- type
- confidence
- status
- valid from
- valid until
- created/updated timestamp
- source message
- supersedes
- superseded by

Status should have clear visual treatment:

ACTIVE
SUPERSEDED
EXPIRED
ARCHIVED
FORGOTTEN

Avoid relying on color alone.

# 14. Memory Timeline

Create a reusable interactive timeline.

Requirements:

- chronological ordering
- current state emphasis
- historical states remain visible
- expandable events
- metadata
- smooth transitions

Example:

```text
2025
Python
  │
2026
Java
  │
2026
C++
  │
NOW
```

The timeline must make temporal reasoning obvious.

# 15. Conflict UI

Create a reusable `ConflictView`.

Show:

- competing memories
- memory IDs
- timestamps
- confidence
- status
- temporal validity
- relationship between memories

The UI must not independently decide which memory wins.

The AI/backend supplies the state.

# 16. Provenance UI

Create a reusable `ProvenancePanel`.

It should answer:

> Which stored memories were used for this answer?

For each memory display:

- memory ID
- reason
- confidence
- status
- optionally timestamp

Use an expandable interaction.

Example:

```text
WHY THIS ANSWER?  ↓

✓ mem_03_cpp
  Current state match
  94%

✓ mem_02_java
  Historical context
  91%
  Superseded
```

Provenance must come from application data.

Never ask the LLM to invent memory IDs.

# 17. Mock API Layer

Because the backend is still being built, create a frontend adapter.

Example:

```text
src/
  lib/
    api/
      client.js
      mock.js
      types.js
```

The UI should call functions such as:

```js
sendMessage(userId, query)
getMemories(userId)
getTimeline(userId)
getMemory(memoryId)
```

The UI must not directly contain fake data inside dozens of components.

Centralize mock data.

Later:

```text
mock.js
     ↓
backend API client
```

The component layer should not need to change.

# 18. Initial Mock Scenarios

Build mock data specifically around the project's judging scenarios.

## Scenario 1 — Current state

```text
Python → Java → C++
```

Question:

> What programming language am I currently using?

Expected answer:

C++

Relevant current memory:

`mem_03_cpp`

## Scenario 2 — Historical state

Question:

> What language was I using before C++?

Expected:

Java

## Scenario 3 — Timeline

Question:

> Show how my programming language changed.

Display:

Python → Java → C++

## Scenario 4 — Contradiction

Memories:

```text
mem_contra_cat
pet = cat

mem_contra_dog
pet = dog
```

Display the contradiction and the relevant temporal/context information.

## Scenario 5 — Forgotten memory

A forgotten memory must not appear as an active retrieval source.

## Scenario 6 — User isolation

User A and User B must have separate memory sets.

This should be demonstrable from the UI.

# 19. Data Contract

The frontend should support responses shaped approximately like:

```json
{
  "answer": "You're currently using C++.",
  "sources": [
    {
      "memory_id": "mem_03_cpp",
      "reason": [
        "semantic_match",
        "current_state_match",
        "active_memory"
      ],
      "confidence": 0.94,
      "status": "active"
    }
  ],
  "uncertainty": 0.06,
  "conflict_detected": false
}
```

Do not hardcode assumptions that the backend cannot satisfy.

Keep types/interfaces centralized so the contract can evolve.

# 20. Component Architecture

Use reusable components.

Suggested structure:

```text
src/
├── components/
│   ├── ui/
│   ├── layout/
│   ├── chat/
│   ├── memory/
│   ├── timeline/
│   ├── provenance/
│   └── conflict/
│
├── pages/
│   ├── Landing.jsx
│   ├── Assistant.jsx
│   ├── Timeline.jsx
│   └── MemoryExplorer.jsx
│
├── data/
│   └── mock/
│
├── hooks/
│
├── lib/
│   ├── api/
│   └── utils/
│
├── styles/
│
├── App.jsx
└── main.jsx
```

Exact structure may change if there is a strong technical reason.

Avoid giant components.

# 21. Technology

Preferred:

- React
- Vite
- modern JavaScript/TypeScript
- Tailwind CSS if useful
- Framer Motion / Motion for animation
- Lucide or similarly restrained icon system

Do not add libraries simply because they are popular.

Every dependency should have a purpose.

Do not introduce a heavy 3D engine unless the visual result genuinely benefits from it.

# 22. Responsive Design

The experience must work on:

- desktop
- laptop
- tablet
- mobile

Desktop is the primary hackathon presentation target.

Mobile should not merely shrink the desktop layout.

Use:

- drawers
- collapsible panels
- stacked cards
- horizontal timeline scrolling where appropriate

No horizontal page overflow.

# 23. Accessibility

Include:

- keyboard navigation
- visible focus states
- semantic HTML
- accessible labels
- sufficient contrast
- reduced-motion support
- no information conveyed by color alone

If the user prefers reduced motion, respect `prefers-reduced-motion`.

# 24. Performance

Avoid:

- huge image assets
- unnecessary JavaScript
- dozens of simultaneous animations
- continuous expensive canvas effects
- excessive blur filters

Animations should remain smooth on normal laptops.

Use lazy loading where appropriate.

# 25. Security / Trust

The frontend must never imply that mock data is real backend data.

During development, clearly isolate mock mode.

Do not expose API keys.

Do not put Gemini credentials in frontend code.

The browser must never receive `GEMINI_API_KEY`.

# 26. Error States

Implement polished states for:

- loading
- empty memory
- no relevant memory
- conflict detected
- API failure
- backend unavailable
- unknown memory
- user with no history

Example:

```text
NO RELEVANT MEMORY

I couldn't find a stored memory relevant
to this question.

Try asking about something you've previously
shared with Anamnesis.
```

Do not make empty states look like errors.

# 27. Visual Quality Rules

Before considering the frontend complete:

- no placeholder-looking UI
- no default browser buttons
- no inconsistent spacing
- no random colors
- no excessive rounded cards
- no generic dashboard aesthetic
- no unnecessary gradients everywhere
- no stock "AI brain" imagery
- no lorem ipsum
- no fake testimonials
- no fabricated statistics
- no invented product claims

Every visible element should have a reason to exist.

# 28. Demo Mode

Create a presentation-friendly demo mode.

The judge should be able to quickly demonstrate:

1. Ask about current programming language.
2. Show C++ as current.
3. Open provenance.
4. Open timeline.
5. Ask about historical language.
6. Show contradiction.
7. Show forgotten memory.
8. Switch user and demonstrate isolation.

Provide convenient UI controls for switching between demo scenarios if useful.

Do not hide the actual architecture behind a fake scripted experience.

# 29. Frontend Definition of Done

### Build

- React/Vite app builds successfully.
- No runtime console errors.
- No broken routes.
- No missing assets.

### Visual

- Landing page is polished.
- Assistant page is polished.
- Motion feels intentional.
- Typography hierarchy is strong.
- Responsive layouts work.

### Product

- Chat works against mock API.
- Memory cards work.
- Timeline works.
- Provenance works.
- Conflict UI works.
- Forgotten state is represented.
- User isolation is demonstrable.

### Integration

- Mock API contract is centralized.
- Frontend can later replace mock API with backend API without rewriting components.
- No backend implementation has been duplicated in frontend.

### Accessibility

- Keyboard navigation works.
- Focus states exist.
- Reduced motion is respected.
- Color is not the only state indicator.

### Code quality

- Components are reusable.
- No giant monolithic page component.
- No duplicated mock data.
- No secrets.
- No unexplained dependencies.

# 30. Git Rules

Work only on the frontend feature branch.

Recommended:

```bash
git checkout -b feature/frontend
```

Do NOT push directly to `main`.

Before committing:

```bash
git status
git diff
```

Verify:

```bash
npm run build
```

If tests/lint scripts exist, run them too.

Commit with a meaningful message:

```bash
git add frontend docs/Epoquesque_Frontend_Design_Playbook.md
git commit -m "Build AnamnesisAI frontend experience"
git push -u origin feature/frontend
```

If the team's existing branch convention requires a different branch name, follow that convention.

# 31. Handoff to Backend

When the backend becomes available:

1. Confirm the API contract.
2. Map backend responses to the frontend adapter.
3. Replace mock implementation.
4. Keep component interfaces stable.
5. Test user isolation.
6. Test current/historical/timeline queries.
7. Test provenance.
8. Test conflicts.
9. Test forgotten memories.
10. Test backend failure states.

Do not rewrite the UI merely because the backend arrives.

# 32. Instructions for Antigravity

You are the frontend implementation agent for AnamnesisAI.

FIRST:

1. Inspect the repository.
2. Read `docs/Epoquesque_AI_Agent_Engineering_Playbook.md`.
3. Read `docs/Epoquesque_Frontend_Design_Playbook.md`.
4. Confirm that no frontend currently exists.
5. Inspect the existing AI/Agent implementation.
6. Do not modify AI/Agent logic unless required for a clearly defined frontend integration boundary.

THEN:

1. Initialize the frontend from scratch.
2. Use React + Vite.
3. Establish the design tokens first.
4. Build the landing page.
5. Build the assistant application.
6. Build memory visualization.
7. Build timeline.
8. Build provenance.
9. Build conflict visualization.
10. Build mock API.
11. Add responsive behavior.
12. Add accessibility.
13. Run the application.
14. Inspect the rendered UI.
15. Iterate on visual quality.
16. Run build/lint/tests.
17. Report exactly what changed.

IMPORTANT:

Do not stop after generating static-looking components.

Actually run the frontend and inspect the rendered result.

Prioritize visual quality and coherent motion.

Do not implement PostgreSQL, FastAPI, pgvector, authentication, or Gemini credentials.

The backend is under development and will be integrated later.

# 33. Final Design Principle

Anamnesis should make the judge feel that they are not looking at:

> "another chatbot with a vector database."

They should be able to SEE:

> memory being formed → memory changing → memory becoming historical → conflicts emerging → the current state being selected → the answer being explained.

The interface itself should communicate the project's core innovation.
