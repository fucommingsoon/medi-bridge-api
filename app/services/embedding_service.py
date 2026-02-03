"""Bailian Embedding Service"""
import os

import dashscope
from dashscope import TextEmbedding

from app.core.config import settings
from app.core.exceptions import VectorSearchError


class EmbeddingService:
    """Bailian text embedding service"""

    def __init__(self):
        self._initialized = False
        self.model = "text-embedding-v4"

    def _ensure_initialized(self):
        """Ensure API Key is configured"""
        if self._initialized:
            return

        # Set API Key
        if settings.BAILIAN_API_KEY:
            dashscope.api_key = settings.BAILIAN_API_KEY
        else:
            # Try to get from environment variable BAILIAN_API_KEY
            api_key = os.environ.get("BAILIAN_API_KEY")
            if not api_key:
                raise VectorSearchError("BAILIAN_API_KEY not configured")
            dashscope.api_key = api_key

        self._initialized = True

    async def embed_text(self, text: str) -> list[float]:
        """
        Convert text to embedding vector

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        self._ensure_initialized()

        if not text or not text.strip():
            raise VectorSearchError("Input text cannot be empty")

        try:
            resp = TextEmbedding.call(
                model=self.model,
                input=text,
            )

            if resp.status_code != 200:
                raise VectorSearchError(
                    f"Embedding API error: {resp.message} (code: {resp.status_code})"
                )

            # Extract embedding vector
            embedding = resp.output["embeddings"][0]["embedding"]
            return embedding

        except VectorSearchError:
            raise
        except Exception as e:
            raise VectorSearchError(f"Embedding failed: {str(e)}")

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Convert multiple texts to embedding vectors (batch processing)

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors
        """
        self._ensure_initialized()

        if not texts:
            raise VectorSearchError("Input texts list cannot be empty")

        try:
            resp = TextEmbedding.call(
                model=self.model,
                input=texts,
            )

            if resp.status_code != 200:
                raise VectorSearchError(
                    f"Batch embedding API error: {resp.message} (code: {resp.status_code})"
                )

            # Extract embedding vectors
            embeddings = [item["embedding"] for item in resp.output["embeddings"]]
            return embeddings

        except VectorSearchError:
            raise
        except Exception as e:
            raise VectorSearchError(f"Batch embedding failed: {str(e)}")


# Global service instance (lazy initialization)
embedding_service = EmbeddingService()
