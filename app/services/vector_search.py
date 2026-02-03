"""Vector Search Service"""

from app.models.vector_db import qdrant_client
from app.core.config import settings
from app.core.exceptions import VectorSearchError
from app.services.embedding_service import embedding_service


class VectorSearchService:
    """Vector search service"""

    def __init__(self):
        self.client = qdrant_client

    async def search(self, query: str, limit: int | None = None) -> list[dict]:
        """
        Execute vector search

        Args:
            query: Query text
            limit: Number of results to return

        Returns:
            List of matched medical information
        """
        try:
            limit = limit or settings.TOP_K_RESULTS

            # Convert query text to embedding vector
            query_vector = await embedding_service.embed_text(query)

            # Execute vector search
            results = self.client.client.search(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit,
                score_threshold=settings.SIMILARITY_THRESHOLD,
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                })

            return formatted_results

        except VectorSearchError:
            raise
        except Exception as e:
            raise VectorSearchError(f"Vector search failed: {str(e)}")

    async def health_check(self) -> bool:
        """Check vector database connection status"""
        return self.client.health_check()


# Global service instance
vector_search_service = VectorSearchService()
