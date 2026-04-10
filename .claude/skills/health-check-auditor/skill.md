---
name: health-check-auditor
description: >
  Use this skill when the user says "check system health", "verify services", "diagnose issues",
  "is everything running", or wants a comprehensive system status report.
  Triggers include: "health check", "system status", "verify setup", "diagnostic report",
  "what's broken", "check connectivity".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "medium"
  category: "monitoring"
---

# Health Check Auditor

## Role

You are an expert in diagnosing the health of this anti-fraud RAG system. Your job is to run comprehensive checks on all system components and produce a diagnostic report identifying any issues.

---

## System Components to Check

```
┌─────────────────────────────────────────────────────────────────┐
│                     Health Check Matrix                          │
├─────────────────────────────────────────────────────────────────┤
│  Component          │ Check Method              │ Expected      │
├─────────────────────┼───────────────────────────┼───────────────┤
│  API Server         │ GET /health               │ 200 OK        │
│  Database           │ pg_isready                │ accepting     │
│  pgvector Extension │ SQL query                 │ installed     │
│  Tables Exist       │ SQL query                 │ cases, tips   │
│  Embedding Service  │ POST /v1/embeddings       │ 200 OK        │
│  Environment Vars   │ Check required vars       │ all set       │
└─────────────────────┴───────────────────────────┴───────────────┘
```

---

## Required Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMBEDDING_MODEL_URL` | Yes | — | Embedding API endpoint |
| `EMBEDDING_MODEL_API_KEY` | Yes | — | API key for embedding service |
| `EMBEDDING_DIMENSION` | No | 1536 | Vector dimension |
| `HIGH_RISK_THRESHOLD` | No | 0.85 | Risk score threshold |
| `API_KEY` | No | your-secret-api-key | API authentication key |
| `DATABASE_URL` | No | postgresql+asyncpg://... | Database connection string |

---

## Workflow

1. **Check Environment Variables** — Verify all required vars are set:
   ```bash
   echo $EMBEDDING_MODEL_URL
   echo $EMBEDDING_MODEL_API_KEY
   ```
2. **Check Docker Services** — Verify containers are running:
   ```bash
   docker compose ps
   ```
3. **Check API Health** — Call the health endpoint:
   ```bash
   curl -s http://localhost:8000/health | jq
   ```
4. **Check Database Connection** — Test connectivity:
   ```bash
   docker compose exec db pg_isready -U antifraud_user -d antifraud_db
   ```
5. **Check pgvector Extension** — Verify extension is installed:
   ```bash
   docker compose exec db psql -U antifraud_user -d antifraud_db -c "\dx pgvector"
   ```
6. **Check Tables Exist** — Verify schema is initialized:
   ```bash
   docker compose exec db psql -U antifraud_user -d antifraud_db -c "\dt"
   ```
7. **Check Embedding Service** — Test embedding API:
   ```bash
   curl -X POST "$EMBEDDING_MODEL_URL" \
     -H "Authorization: Bearer $EMBEDDING_MODEL_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"input": "test", "model": "text-embedding-ada-002"}'
   ```
8. **Generate Report** — Compile results into a summary.

---

## Report Template

```
═══════════════════════════════════════════════════════════
              ANTI-FRAUD RAG SYSTEM HEALTH REPORT
═══════════════════════════════════════════════════════════

[✓] Environment Variables
    - EMBEDDING_MODEL_URL: https://...
    - EMBEDDING_MODEL_API_KEY: ***set***

[✓] Docker Services
    - app: running (healthy)
    - db: running (healthy)

[✓] API Server
    - Health endpoint: 200 OK
    - Uptime: 2h 34m

[✓] Database
    - Connection: OK
    - pgvector extension: installed
    - Tables: cases (125 rows), tips (432 rows)

[✓] Embedding Service
    - API reachable: yes
    - Response time: 145ms

═══════════════════════════════════════════════════════════
STATUS: ALL SYSTEMS HEALTHY
═══════════════════════════════════════════════════════════
```

---

## Common Issues & Solutions

| Issue | Symptom | Fix |
|-------|---------|-----|
| API not responding | curl timeout | Check `make docker-logs` for errors |
| pgvector missing | `\dx` shows no pgvector | Use correct Docker image: `pgvector/pgvector:pg17-trixie` |
| Tables missing | `\dt` returns empty | Run `make db-init` |
| Embedding API failing | 401/403 errors | Verify `EMBEDDING_MODEL_API_KEY` is valid |
| DB connection refused | `could not connect` | Check db container health, restart with `make docker-up` |

---

## Files to Reference

- `docker-compose.yml` — Service definitions
- `antifraud_rag/main.py` — Health endpoint implementation
- `antifraud_rag/core/config.py` — Settings and env var definitions
- `antifraud_rag/db/session.py` — Database connection setup
- `scripts/init_db.py` — Database initialization

---

## Constraints

- NEVER expose API keys in output — mask them with `***`.
- DO NOT run destructive commands (e.g., database reset) without explicit user confirmation.
- Anti-Loop: If a check fails 3 times, report the failure and ask user for guidance.
- Always check services before checking application-level health.

---

## Examples

**User:** "Run a health check on the system"

**Assistant:**

Thinking:
1. Check environment variables are set.
2. Check Docker containers are running.
3. Test API health endpoint.
4. Verify database connectivity and pgvector.
5. Test embedding service.
6. Generate diagnostic report.

Uses the `bash` tool with command `docker compose ps`
Uses the `bash` tool with command `curl -s http://localhost:8000/health`
Uses the `bash` tool with command `docker compose exec db psql -U antifraud_user -d antifraud_db -c "\dx pgvector"`
