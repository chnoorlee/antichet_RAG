---
name: pytest-test-runner
description: >
  Use this skill when the user says "run tests", "pytest", "test failing",
  "make test", "run the test suite", or when test output shows failures.
  Triggers include: "make test", "pytest tests/", "test error", "test coverage",
  "test_api", "test-services".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "high"
  category: "testing"
---

# Pytest Test Runner

## Role

You are an expert in running and debugging pytest tests for this FastAPI/RAG project. Your job is to execute tests with proper environment setup, diagnose failures, and suggest targeted fixes.

---

## Workflow

1. **Set Environment** — Tests require mock environment variables: `EMBEDDING_MODEL_URL` and `EMBEDDING_MODEL_API_KEY`.
2. **Run Tests** — Execute `make test` or specific test targets (e.g., `make test-api`).
3. **Analyze Failures** — Parse the pytest output to identify:
   - Async test issues (missing `pytest-asyncio`)
   - Import errors (missing dependencies)
   - Database connection issues (requires running services)
   - Assertion failures (logic bugs)
4. **Fix Issues** — Apply targeted fixes:
   - For import/module errors: check `pyproject.toml` dependencies
   - For async errors: ensure `@pytest.mark.asyncio` decorators present
   - For database errors: verify Docker services are running (`make docker-up`)
   - For logic failures: read the source file and fix the implementation
5. **Re-run** — Execute the specific test command again to verify the fix.
6. **Report** — Summarize test results and any remaining failures.

---

## Project Test Commands

```bash
# Full test suite
make test

# Specific test targets
make test-api         # API endpoint tests (test_analyze.py, test_data.py, test_main.py)
make test-services    # Service layer tests (test_retrieval.py, test_embedding.py)
make test-config      # Config/settings tests (test_config.py)
make test-schemas     # Schema validation tests (test_schemas.py)
make test-cov        # With coverage report
make test-unit       # Unit tests only (not integration)

# Run specific tests with args
make test ARGS="-v -k test_analyze"
```

## Test Files Location

- `tests/conftest.py` — Shared fixtures
- `tests/test_main.py` — App startup/health tests
- `tests/test_analyze.py` — `/api/v1/analyze` endpoint tests
- `tests/test_data.py` — `/api/v1/data/` endpoint tests
- `tests/test_retrieval.py` — RetrievalService tests
- `tests/test_embedding.py` — EmbeddingService tests
- `tests/test_config.py` — Settings validation tests
- `tests/test_schemas.py` — Pydantic schema tests

---

## Constraints

- NEVER run tests without setting the required env vars (done automatically via Makefile).
- DO NOT modify `conftest.py` unless explicitly requested — it contains shared fixtures.
- Anti-Loop: If the same test fails 3 times, STOP and ask the user for guidance.
- For database integration tests, ensure Docker services are running first.

---

## Examples

**User:** "Run the API tests and fix any failures"

**Assistant:**

Thinking:
1. Run `make test-api` to see which tests fail.
2. Analyze the failure output to identify the root cause.
3. Read the relevant source file to understand the issue.
4. Apply the fix.
5. Re-run `make test-api` to verify.

Uses the `bash` tool with command `make test-api`
