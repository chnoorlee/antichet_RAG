# AGENTS.md — Anti-Fraud RAG System

## Project

FastAPI-based Anti-Fraud RAG system with hybrid search (BM25 + vector + RRF), PostgreSQL/pgvector backend, Docker Compose deployment.

## Quick Commands

```bash
make install       # Install deps via uv
make dev           # Local dev server (hot reload on port 8000)
make docker-up     # Start all services (app + postgres)
make db-init       # Init database (pgvector extension + tables)
make lint          # ruff check
make fmt           # ruff format + fix
make test          # Run tests (sets mock env vars automatically)
make ci            # lint + test (mirrors CI)
```

## Required Environment Variables

```bash
EMBEDDING_MODEL_URL=https://your-embedding-api.com/v1/embeddings
EMBEDDING_MODEL_API_KEY=your-key
# Optional (have defaults):
# EMBEDDING_DIMENSION=1536
# HIGH_RISK_THRESHOLD=0.85
# API_KEY=your-secret-key
```

Tests automatically set mock values for these vars.

## Architecture

```
app/
├── main.py              # FastAPI app, API key auth middleware
├── api/v1/
│   ├── analyze.py        # POST /api/v1/analyze (core RAG endpoint)
│   └── data.py          # POST /api/v1/data/{case,tip}
├── core/config.py        # Settings via pydantic-settings
├── db/
│   ├── models.py         # Case, Tip (SQLAlchemy + pgvector)
│   └── session.py       # Async SQLAlchemy engine
└── services/
    ├── retrieval.py      # RRF fusion, BM25, vector search
    └── embedding.py      # Embedding API client
```

## Key Implementation Details

- **RRF fusion**: `k=60`, combines BM25 + vector rankings
- **High-risk threshold**: Score > 0.85 returns `Direct_Hit` (blocked), otherwise returns `RAG_Prompt`
- **Database**: Uses pgvector for ANN search, TSVECTOR for full-text (currently english tokenizer; zhparser commented out in `init_db.py`)
- **Auth**: All endpoints except `/health` require `X-API-Key` header
- **Async**: SQLAlchemy with asyncpg driver

## Running Tests

```bash
# Full suite
make test

# Specific test files
make test-api      # API endpoint tests
make test-services # Retrieval + embedding services
make test-config   # Settings validation
make test-schemas  # Pydantic schema tests
```

## Docker Development

```bash
make docker-build  # Rebuild after deps change
make docker-logs   # Tail app logs
make docker-logs SVC=db  # Tail database logs
```

Database reset: `make docker-down -v && make docker-up && make db-init`
