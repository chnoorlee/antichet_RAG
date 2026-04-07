import asyncio
import os
import sys

# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.db.models import Base
from app.db.session import engine


async def init_db():
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
