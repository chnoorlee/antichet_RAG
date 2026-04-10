---
name: data-bulk-importer
description: >
  Use this skill when the user says "import data", "bulk insert", "load cases", "add tips from file",
  "seed database", or wants to import cases/tips from JSON/CSV files.
  Triggers include: "import cases", "bulk load", "database seeding", "json to database",
  "csv import", "load test data".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "medium"
  category: "data-management"
---

# Data Bulk Importer

## Role

You are an expert in bulk importing data into this anti-fraud RAG system. Your job is to import cases and tips from JSON/CSV files, generate embeddings, and populate the database with proper validation.

---

## Data Models

### Case Model
```python
class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100))
    risk_score = Column(Numeric(3, 2), default=0.0)
    embedding = Column(Vector(1536))
    content_tsv = Column(TSVECTOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Tip Model
```python
class Tip(Base):
    __tablename__ = "tips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(200))
    embedding = Column(Vector(1536))
    content_tsv = Column(TSVECTOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Expected Input Formats

### JSON Format (Cases)
```json
[
  {
    "title": "Investment Fraud Case #123",
    "description": "Victim lost $50,000 to fake investment scheme...",
    "category": "investment_fraud",
    "risk_score": 0.92
  }
]
```

### JSON Format (Tips)
```json
[
  {
    "case_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "Suspect used multiple phone numbers...",
    "source": "anonymous_tip"
  }
]
```

### CSV Format
```csv
title,description,category,risk_score
"Investment Fraud #123","Victim lost $50k...","investment_fraud",0.92
```

---

## Workflow

1. **Read Input File** — Use `read` to load the JSON/CSV file.
2. **Validate Schema** — Check that required fields are present:
   - Cases: `title`, `description` (required); `category`, `risk_score` (optional)
   - Tips: `case_id`, `content` (required); `source` (optional)
3. **Check Database Connection** — Verify services are running:
   ```bash
   make docker-up
   ```
4. **Generate Embeddings** — For each record, call the embedding service to generate vectors.
5. **Insert Records** — Use SQLAlchemy async session to bulk insert:
   ```python
   session.add_all(records)
   await session.commit()
   ```
6. **Verify Import** — Query the database to confirm records were added:
   ```bash
   docker compose exec db psql -U antifraud_user -d antifraud_db -c "SELECT COUNT(*) FROM cases;"
   ```
7. **Report Summary** — Output count of imported records and any errors.

---

## Import Script Pattern

```python
import asyncio
import json
from antifraud_rag.db.session import async_session
from antifraud_rag.db.models import Case
from antifraud_rag.services.embedding import embedding_service

async def import_cases(filepath: str):
    with open(filepath) as f:
        data = json.load(f)

    async with async_session() as session:
        for item in data:
            embedding = await embedding_service.get_embeddings(item["description"])
            case = Case(
                title=item["title"],
                description=item["description"],
                category=item.get("category"),
                risk_score=item.get("risk_score", 0.0),
                embedding=embedding,
            )
            session.add(case)
        await session.commit()
    print(f"Imported {len(data)} cases")
```

---

## Files to Reference

- `antifraud_rag/db/models.py` — Case and Tip model definitions
- `antifraud_rag/db/session.py` — Async session factory
- `antifraud_rag/services/embedding.py` — Embedding service client
- `scripts/init_db.py` — Database initialization pattern

---

## Constraints

- NEVER import data without validating the schema first.
- DO NOT overwrite existing records — check for duplicates by title/content hash.
- Anti-Loop: If embedding API fails 3 times, STOP and ask user to verify API configuration.
- Always backup or confirm before bulk insert (no dry-run mode exists yet).
- Embeddings must match `EMBEDDING_DIMENSION` (default 1536).

---

## Examples

**User:** "Import these cases from cases.json into the database"

**Assistant:**

Thinking:
1. Read `cases.json` to understand the data structure.
2. Validate each record has required fields.
3. Check that Docker services are running.
4. Generate embeddings for each case description.
5. Bulk insert into the database.
6. Verify the import succeeded.

Uses the `read` tool with filePath `cases.json`
Uses the `bash` tool with command `make docker-up`
Uses the `bash` tool with command `python scripts/import_cases.py cases.json`
