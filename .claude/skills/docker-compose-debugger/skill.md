---
name: docker-compose-debugger
description: >
  Use this skill when the user says "docker compose not working", "container won't start",
  "database connection failed", "Docker health check failing", or when `make docker-up` fails.
  Triggers include: "docker error", "container unhealthy", "pgvector not loading",
  "env var missing in container", "docker logs error".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "high"
  category: "devops"
---

# Docker Compose Debugger

## Role

You are an expert in debugging Docker Compose setups for this anti-fraud RAG system. Your job is to diagnose container failures, database connectivity issues, and environment configuration problems.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
├─────────────────────────────────────────────────────────┤
│  app:8000                    db:5432                    │
│  ┌──────────────┐           ┌──────────────────┐       │
│  │ FastAPI App  │──────────▶│ PostgreSQL +     │       │
│  │ (Python 3.10)│  asyncpg  │ pgvector pg17    │       │
│  └──────────────┘           └──────────────────┘       │
│       ▲                                                 │
│       │ HTTP (X-API-Key)                               │
└───────┼─────────────────────────────────────────────────┘
        │
    External Embedding API
```

## Key Configuration

- **App port**: 8000 (configurable via `PORT`)
- **DB port**: 5432
- **DB credentials**: `antifraud_user` / `antifraud_pass` / `antifraud_db`
- **DB image**: `pgvector/pgvector:pg17-trixie`
- **Health check**: `pg_isready -U antifraud_user -d antifraud_db`

---

## Workflow

1. **Check Container Status** — Run `docker compose ps` to see which containers are unhealthy or exited.
2. **Check Logs** — Run `make docker-logs` or `docker compose logs <service>` to see error messages.
3. **Verify Environment Variables** — Check that required env vars are set:
   - `EMBEDDING_MODEL_URL`
   - `EMBEDDING_MODEL_API_KEY`
4. **Check Database Health** — Verify pgvector extension and table initialization:
   ```bash
   docker compose exec db psql -U antifraud_user -d antifraud_db -c "\dx"
   ```
5. **Verify Network Connectivity** — Test if app can reach db:
   ```bash
   docker compose exec app python -c "import asyncpg; print('OK')"
   ```
6. **Check Volume Permissions** — Ensure `pgdata` volume is accessible.
7. **Apply Fixes** — Based on diagnosis:
   - Restart specific service: `docker compose restart <service>`
   - Rebuild after code change: `make docker-build`
   - Full reset: `make docker-down -v && make docker-up && make db-init`

---

## Common Issues & Solutions

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| `db` unhealthy | pgvector extension missing | Use `pgvector/pgvector:pg17-trixie` image |
| `app` exits immediately | Missing env vars | Check `.env` file or export vars manually |
| Connection refused | db not ready yet | `depends_on` condition should wait for healthcheck |
| Port conflict | 5432 or 8000 in use | Change port in `docker-compose.yml` or stop conflicting service |
| Permission denied | Volume mount issue | Run `docker volume prune` and recreate |
| Embedding API timeout | Network/firewall | Verify `EMBEDDING_MODEL_URL` is accessible from container |

---

## Files to Check

- `docker-compose.yml` — Service definitions and configuration
- `Dockerfile` — App container build instructions
- `.env` or `.env.example` — Environment variable templates
- `scripts/init_db.py` — Database initialization script
- `Makefile` — `docker-up`, `docker-down`, `docker-build`, `docker-logs` targets

---

## Constraints

- NEVER run `docker system prune -a` or `docker volume rm` without explicit user confirmation.
- DO NOT modify `docker-compose.yml` without understanding the full service dependencies.
- Anti-Loop: If the same error persists after 3 fix attempts, ask the user for the exact error message.
- Always check logs before making changes.

---

## Examples

**User:** "make docker-up fails with 'container app exited with code 1'"

**Assistant:**

Thinking:
1. Check container status with `docker compose ps`.
2. Check app logs with `docker compose logs app`.
3. Identify the error (likely missing env var or import error).
4. Fix the issue and restart.

Uses the `bash` tool with command `docker compose logs app --tail 50`
Uses the `bash` tool with command `docker compose ps`
Uses the `read` tool with filePath `docker-compose.yml`
