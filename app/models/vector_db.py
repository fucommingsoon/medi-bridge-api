"""Vector Database Client"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.core.config import settings
from app.core.exceptions import QdrantConnectionError


class QdrantClientWrapper:
    """Qdrant client wrapper"""

    def __init__(self):
        self._client: QdrantClient | None = None

    @property
    def client(self) -> QdrantClient:
        """Get Qdrant client instance"""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> QdrantClient:
        """Create Qdrant client"""
        try:
            if settings.QDRANT_API_KEY:
                client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY,
                )
            else:
                client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                )
            return client
        except Exception as e:
            raise QdrantConnectionError(f"Qdrant connection failed: {str(e)}")

    def create_collection(self) -> None:
        """Create collection"""
        self.client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=settings.VECTOR_SIZE, distance=Distance.COSINE
            ),
        )

    def health_check(self) -> bool:
        """Health check"""
        try:
            collections = self.client.get_collections()
            return True
        except Exception:
            return False


# Global instance
qdrant_client = QdrantClientWrapper()
