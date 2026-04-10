import asyncio
import os
import sys

# Add the project root to sys.path to allow imports from antifraud_rag
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from antifraud_rag.core.config import Settings
from antifraud_rag.db.models import Base


async def init_db():
    settings = Settings()
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        # Create pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # In a real environment with zhparser, we would add:
        # await conn.execute(text("CREATE EXTENSION IF NOT EXISTS zhparser"))
        # await conn.execute(text("CREATE TEXT SEARCH CONFIGURATION zhparser (PARSER = zhparser)"))

        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
