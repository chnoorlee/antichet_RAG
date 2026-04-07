# AGENT.md — Anti-Fraud RAG System

## Project Overview

FastAPI-based Anti-Fraud RAG system with hybrid search (BM25 + vector + RRF), PostgreSQL/pgvector backend, and Docker Compose deployment.

## Quick Start

```bash
make install          # install dependencies
make docker-up       # start services
make db-init         # init database
make dev             # local dev server
make test            # run tests
make lint            # lint code
```

## All Targets

| Target | Description | When to Use |
|--------|-------------|-------------|
| `make install` | Install deps via uv | After clone or dependency changes |
| `make dev` | Start dev server with hot reload | Local development |
| `make docker-build` | Build Docker image with uv | Before deployment or after deps change |
| `make docker-up` | Start all services | Start containerized dev/deploy |
| `make docker-down` | Stop and remove services | Stop environment |
| `make docker-logs` | Tail app logs (SVC=db for db logs) | Debug running services |
| `make db-init` | Init DB (pgvector + tables) | First start or DB reset |
| `make lint` | ruff check | Before commits |
| `make fmt` | ruff format + fix | Format code during dev |
| `make test` | pytest tests/ -v | Run test suite |
| `make clean` | Remove caches and artifacts | Cleanup or fix build issues |
| `make ci` | lint + test | Simulate CI locally |

## Dev Tips

- **Dependency changes**: Edit `pyproject.toml`, then `make install` locally and `make docker-build` for container.
- **Database reset**: `make docker-down -v` (remove volumes) + `make docker-up` + `make db-init`.
- **Linting before PR**: Run `make ci` to mirror CI pipeline locally.
- **Env vars**: Copy `.env.example` to `.env` and fill in values before running `make dev` or `make db-init`.
- **Docker logs**: `make docker-logs` shows app logs; `make docker-logs SVC=db` shows database logs.
