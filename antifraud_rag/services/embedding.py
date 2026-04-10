import logging
from typing import List

import httpx

from antifraud_rag.core.config import Settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, settings: Settings):
        self.url = settings.EMBEDDING_MODEL_URL
        self.api_key = settings.EMBEDDING_MODEL_API_KEY
        self.model = settings.EMBEDDING_MODEL_NAME

    async def get_embeddings(self, text: str) -> List[float]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"input": text, "model": self.model},
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                # Assuming OpenAI compatible response format
                return data["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise RuntimeError(f"Embedding API error: {str(e)}")
