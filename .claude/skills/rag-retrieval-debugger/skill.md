---
name: rag-retrieval-debugger
description: >
  Use this skill when the user says "debug retrieval", "check RRF", "fix search",
  "analyze search results", "BM25 not working", "vector search broken",
  or when the /api/v1/analyze endpoint returns unexpected results.
  Triggers include: "retrieval issue", "hybrid search not working", "RRF fusion error",
  "search returning wrong results", "embedding mismatch".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "high"
  category: "debugging"
---

# RAG Retrieval Debugger

## Role

You are an expert in debugging the hybrid retrieval pipeline (BM25 + vector + RRF fusion) for this anti-fraud RAG system. Your job is to diagnose and fix issues with search relevance, ranking, and score calculation.

---

## Retrieval Pipeline Overview

```
Query Text
    │
    ├──► BM25 Search ──────► Case IDs + BM25 scores
    │                              │
    ▼                              ▼
Embedding API ◄────────────────────┤
    │                              │
    ▼                              │
Vector Search ──────► Case IDs + Vector scores
    │                              │
    └──────────┬───────────────────┘
               ▼
          RRF Fusion (k=60)
               │
               ▼
        Ranked Results
```

## Key Parameters

- **RRF k**: 60 (configured in `app/services/retrieval.py:55`)
- **High Risk Threshold**: 0.85 (from `settings.HIGH_RISK_THRESHOLD`)
- **Embedding Dimension**: 1536 (default)
- **BM25**: Uses PostgreSQL `ts_rank` with `english` tokenizer

---

## Workflow

1. **Reproduce Issue** — Ask user for the query text that returns unexpected results.
2. **Check Embedding Service** — Verify `embedding_service.get_embeddings()` is working:
   - Test with a simple query
   - Check API key and URL configuration
3. **Debug BM25 Search** — Analyze `search_cases_bm25()`:
   - Check SQL query in `app/services/retrieval.py:29-35`
   - Verify `plainto_tsquery` syntax
   - Check if `content_tsv` index exists
4. **Debug Vector Search** — Analyze `search_cases_vector()`:
   - Verify pgvector extension is installed
   - Check `embedding` column dimension matches query
   - Verify `cosine_distance` calculation
5. **Debug RRF Fusion** — Analyze `rrf_fusion()`:
   - Check if both result sets are being merged
   - Verify score accumulation logic
   - Check rank ordering (1-based vs 0-based)
6. **Verify with Logs** — Add debug logging to trace execution flow.
7. **Fix Issues** — Apply targeted fixes to retrieval service.
8. **Re-test** — Run the analyze endpoint again to verify.

---

## Common Issues & Solutions

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| Empty results | BM25/vector returning no matches | Check query text, verify data exists |
| Wrong ranking | RRF fusion logic incorrect | Verify `k=60` parameter, check rank calculation |
| Low scores | Embedding dimension mismatch | Verify `Vector(1536)` matches API output |
| BM25 failing | `content_tsv` not indexed | Ensure GIN index exists on `content_tsv` |
| Vector failing | pgvector not installed | Check `pip show pgvector` in container |

---

## Files to Debug

- `app/services/retrieval.py` — All retrieval logic (BM25, vector, RRF)
- `app/services/embedding.py` — Embedding API client
- `app/api/v1/analyze.py` — Analyze endpoint (calls retrieval)
- `app/db/models.py` — Case/Tip models with embeddings

---

## Constraints

- NEVER modify `app/api/v1/analyze.py` without understanding the full pipeline.
- DO NOT change `HIGH_RISK_THRESHOLD` or `RRF k` without explicit user approval.
- Anti-Loop: If diagnosis is unclear after 3 iterations, ask the user for more details about the failing query.
- Always test with the same query text that triggered the debug session.

---

## Examples

**User:** "The analyze endpoint returns no results for 'investment fraud' queries"

**Assistant:**

Thinking:
1. Check if cases with "investment fraud" exist in the database.
2. Test embedding generation for the query.
3. Debug BM25 search with raw SQL.
4. Debug vector search with pgvector.
5. Verify RRF fusion is combining results correctly.
6. Fix the identified issue.

Uses the `bash` tool with command `make docker-logs | grep -i "investment"`
Uses the `read` tool with filePath `app/services/retrieval.py`
Uses the `bash` tool with command `psql "postgresql://..." -c "SELECT * FROM cases_table LIMIT 5;"`
