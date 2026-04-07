---
name: sqlalchemy-model-generator
description: >
  Use this skill when the user says "create model", "add database table", "new model",
  "add entity", "create table", or wants to add a new SQLAlchemy model with pgvector.
  Triggers include: "add Case model", "create Tip model", "new database model",
  "add embedding column", "add full-text search".
  When in doubt, use this skill rather than skipping it.
license: MIT
metadata:
  version: "1.0.0"
  author: "Repository Analyst"
  priority: "medium"
  category: "scaffolding"
---

# SQLAlchemy Model Generator

## Role

You are an expert in creating SQLAlchemy models with pgvector support for this anti-fraud RAG project. Your job is to scaffold models with proper vector embeddings, full-text search, and database indexes.

---

## Workflow

1. **Gather Requirements** — Ask the user for:
   - Table name
   - Fields (name, type, nullable, default)
   - Whether it needs vector embedding
   - Whether it needs full-text search (BM25)
2. **Reference Existing Models** — Read `app/db/models.py` to understand:
   - Base class usage
   - UUID primary key pattern
   - Vector embedding column setup
   - TSVector computed column for BM25
   - Index definitions
3. **Generate Model** — Create a new model class following the pattern:
   ```python
   class Xxx(Base):
       __tablename__ = "xxx_table"
       
       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       # ... fields ...
       embedding = Column(Vector(1536))  # Default dimension
       content_tsv = Column(TSVECTOR, Computed("to_tsvector('english', ...)", persisted=True))
       
       __table_args__ = (
           Index("idx_xxx_embedding", "embedding", postgresql_using="ivfflat", ...),
           Index("idx_xxx_tsv", "content_tsv", postgresql_using="gin"),
       )
   ```
4. **Update init_db.py** — If new tables need to be created, update `scripts/init_db.py`.
5. **Create Retrieval Logic** — If the model needs search, add methods to `app/services/retrieval.py`:
   - `search_xxx_vector()` — Vector similarity search
   - `search_xxx_bm25()` — Full-text search
6. **Verify** — Run `make docker-up && make db-init` to apply schema changes.

---

## Model Conventions

### Required Imports
```python
import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Column, Computed, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

### Vector Embedding
- Dimension: `1536` (configurable via `settings.EMBEDDING_DIMENSION`)
- Column: `embedding = Column(Vector(1536))`

### Full-Text Search (BM25)
- TSVector computed column with `to_tsvector('english', ...)`
- GIN index for fast lookups

### Indexes
- Vector: `IVFFlat` index with `vector_cosine_ops`
- TSVector: GIN index

### Timestamps
```python
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## Constraints

- NEVER modify existing models without understanding their relationships.
- Always use UUID for primary keys (consistent with existing models).
- Anti-Loop: If the user provides incomplete field specs, ask for clarification before writing.
- Remember to add `__table_args__` for proper indexes.

---

## Examples

**User:** "Create a Report model for storing user fraud reports with vector search"

**Assistant:**

Thinking:
1. Read existing models to understand patterns.
2. Create Report model with UUID, text fields, vector embedding, and TSVector.
3. Add indexes for vector and full-text search.
4. Update retrieval service if needed.
5. Run db-init to verify.

Uses the `read` tool with filePath `app/db/models.py`
Uses the `edit` tool to add new model
Uses the `bash` tool with command `make docker-up && make db-init`
