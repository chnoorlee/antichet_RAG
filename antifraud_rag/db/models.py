import os
import uuid
from dataclasses import dataclass
from typing import Any, Type

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Column, Computed, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Vector dimension is read from the environment so it matches the configured
# ``Settings.EMBEDDING_DIMENSION`` at import time. Defaults to 1536 (OpenAI
# ``text-embedding-ada-002``). This matters because the pgvector column type
# encodes the dimension in the schema, so the column declaration here must
# match the dimension of the embeddings being stored.
try:
    _EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    if _EMBEDDING_DIM <= 0:
        raise ValueError
except (TypeError, ValueError):
    _EMBEDDING_DIM = 1536


class Case(Base):
    __tablename__ = "cases_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    fraud_type = Column(String(100))
    amount = Column(Numeric(15, 2))
    keywords = Column(ARRAY(String))
    embedding = Column(Vector(_EMBEDDING_DIM))

    # TSVector for full-text search (BM25)
    content_tsv = Column(TSVECTOR, Computed("to_tsvector('simple', description)", persisted=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # ``server_default`` ensures newly inserted rows have a non-null value
    # instead of NULL until the first UPDATE happens.
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_cases_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("idx_cases_tsv", "content_tsv", postgresql_using="gin"),
    )


class Tip(Base):
    __tablename__ = "tips_table"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    keywords = Column(ARRAY(String))
    embedding = Column(Vector(_EMBEDDING_DIM))

    content_tsv = Column(
        TSVECTOR, Computed("to_tsvector('simple', title || ' ' || content)", persisted=True)
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index(
            "idx_tips_embedding",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 50},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("idx_tips_tsv", "content_tsv", postgresql_using="gin"),
    )


@dataclass
class ModelRegistry:
    """Holds dynamically configured Case/Tip model classes and their shared Base."""

    case_model: Type[Any]
    tip_model: Type[Any]
    base: Any


def get_embedding_dimension(model: Type[Any]) -> int:
    """Return the embedding vector dimension declared on a model class."""
    return model.__table__.columns["embedding"].type.dim


def configure_embedding_dimension(dimension: int) -> ModelRegistry:
    """Return a :class:`ModelRegistry` with models using the given embedding dimension.

    When *dimension* matches the default value compiled into the module-level
    ``Case`` and ``Tip`` classes (i.e. ``_EMBEDDING_DIM``), those pre-built
    classes are returned directly.  For any other dimension a fresh
    ``declarative_base`` and a pair of dynamically-created model classes are
    produced so that callers get an isolated schema that can be created via
    ``registry.base.metadata.create_all``.
    """
    if dimension == _EMBEDDING_DIM:
        return ModelRegistry(case_model=Case, tip_model=Tip, base=Base)

    DynBase = declarative_base()

    DynCase = type(
        "Case",
        (DynBase,),
        {
            "__tablename__": "cases_table",
            "__table_args__": (
                Index(
                    f"idx_cases_embedding_{dimension}",
                    "embedding",
                    postgresql_using="ivfflat",
                    postgresql_with={"lists": 100},
                    postgresql_ops={"embedding": "vector_cosine_ops"},
                ),
                Index(f"idx_cases_tsv_{dimension}", "content_tsv", postgresql_using="gin"),
            ),
            "id": Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            "description": Column(Text, nullable=False),
            "fraud_type": Column(String(100)),
            "amount": Column(Numeric(15, 2)),
            "keywords": Column(ARRAY(String)),
            "embedding": Column(Vector(dimension)),
            "content_tsv": Column(
                TSVECTOR,
                Computed("to_tsvector('simple', description)", persisted=True),
            ),
            "created_at": Column(DateTime(timezone=True), server_default=func.now()),
            "updated_at": Column(
                DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
            ),
        },
    )

    DynTip = type(
        "Tip",
        (DynBase,),
        {
            "__tablename__": "tips_table",
            "__table_args__": (
                Index(
                    f"idx_tips_embedding_{dimension}",
                    "embedding",
                    postgresql_using="ivfflat",
                    postgresql_with={"lists": 50},
                    postgresql_ops={"embedding": "vector_cosine_ops"},
                ),
                Index(f"idx_tips_tsv_{dimension}", "content_tsv", postgresql_using="gin"),
            ),
            "id": Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            "title": Column(String(500), nullable=False),
            "content": Column(Text, nullable=False),
            "category": Column(String(100)),
            "keywords": Column(ARRAY(String)),
            "embedding": Column(Vector(dimension)),
            "content_tsv": Column(
                TSVECTOR,
                Computed(
                    "to_tsvector('simple', title || ' ' || content)", persisted=True
                ),
            ),
            "created_at": Column(DateTime(timezone=True), server_default=func.now()),
            "updated_at": Column(
                DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
            ),
        },
    )

    return ModelRegistry(case_model=DynCase, tip_model=DynTip, base=DynBase)
