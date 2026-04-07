---
name: fastapi-endpoint-scaffolder
description: >
  Use this skill when the user says "create endpoint", "add API route", "new API",
  "add endpoint", "create API", or wants to add a new REST endpoint to the project.
  Triggers include: "add /api/v1/xxx endpoint", "create new route", "new FastAPI endpoint".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "medium"
  category: "scaffolding"
---

# FastAPI Endpoint Scaffolder

## Role

You are an expert in creating new FastAPI endpoints following the project's layered architecture (router → service → model). Your job is to scaffold a complete, production-ready endpoint with proper schemas, routing, and tests.

---

## Workflow

1. **Gather Requirements** — Ask the user for:
   - HTTP method (GET, POST, PUT, DELETE)
   - Endpoint path (e.g., `/api/v1/items`)
   - Request/response schema fields
2. **Plan Structure** — Determine which files need to be created/modified:
   - `app/api/v1/{endpoint}.py` — Router with endpoint
   - `app/schemas/{endpoint}.py` — Pydantic request/response models
   - `tests/test_{endpoint}.py` — Unit tests
3. **Read Existing Patterns** — Reference `app/api/v1/analyze.py` and `app/api/v1/data.py` for:
   - Router setup (`APIRouter`)
   - Dependency injection (`Depends(get_db)`)
   - Error handling (`HTTPException`)
   - Schema usage
4. **Create Schema File** — Write Pydantic models with proper type hints and validation.
5. **Create Endpoint File** — Write the router with:
   - Proper async/await patterns
   - Database session management
   - Error handling
   - Logging (`logger = logging.getLogger(__name__)`)
6. **Register Router** — Add to `app/api/v1/__init__.py` or `app/main.py`.
7. **Create Test File** — Write basic test cases following `tests/test_analyze.py` patterns.
8. **Verify** — Run `make lint` and `make test-api` to ensure correctness.

---

## Project Architecture

```
app/
├── main.py              # FastAPI app entry point
├── api/v1/
│   ├── __init__.py      # Router registration
│   ├── analyze.py       # Example: POST /analyze endpoint
│   └── data.py          # Example: POST /data/{case,tip}
├── schemas/
│   └── data.py          # Shared Pydantic models
├── services/
│   ├── retrieval.py      # RetrievalService
│   └── embedding.py     # embedding_service
└── db/
    ├── models.py        # Case, Tip SQLAlchemy models
    └── session.py      # Database session + get_db
```

## Schema Conventions

- Request models: `XxxRequestBody` (inherits `BaseModel`)
- Response models: `XxxResponse` (inherits `BaseModel`)
- Use `Field()` for validation
- Response models should match the API response structure exactly

## Test Conventions

- Mock embedding service calls
- Use `TestClient` for sync tests or `httpx.AsyncClient` for async
- Test both success and error cases
- Follow pattern in `tests/test_analyze.py`

---

## Constraints

- NEVER create files outside the specified directories.
- Always follow the existing code style (async/await, logging, error handling).
- Anti-Loop: If the user provides incomplete requirements, ask clarifying questions before proceeding.
- Always register the new router in `app/api/v1/__init__.py`.

---

## Examples

**User:** "Create a new GET endpoint at /api/v1/status that returns server status"

**Assistant:**

Thinking:
1. Read existing endpoints to understand the pattern.
2. Create schema file `app/schemas/status.py`.
3. Create endpoint file `app/api/v1/status.py`.
4. Register router in `app/api/v1/__init__.py`.
5. Create test file `tests/test_status.py`.
6. Run lint and tests to verify.

Uses the `read` tool with filePath `app/api/v1/analyze.py`
Uses the `write` tool to create new files
Uses the `bash` tool with command `make lint && make test-api`
