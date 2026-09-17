PROJECT RULES

1. main is protected.
2. Every feature gets its own branch.
3. Every PR requires one review.
4. Never change another person's module without discussing it.
5. API contracts must be documented before integration.
6. Database schema changes must be communicated to the team.
7. Never hardcode demo data into production logic.
8. Every memory-backed answer must have provenance.
9. User memory must always be user-scoped.
10. No "works on my laptop" commits.


Branch Structure should become:
main
│
├── feature/memory-engine
├── feature/agent-rag
├── feature/backend-db
└── feature/frontend
