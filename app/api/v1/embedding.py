"""Embedding API Routes"""
from fastapi import APIRouter, HTTPException, Query

from app.models.vector_db import qdrant_client
from app.schemas.embedding import EmbeddingRequest, EmbeddingResponse, StoreRequest, StoreResponse
from app.services.embedding_service import embedding_service
from app.services.vector_search import vector_search_service

router = APIRouter(prefix="/embedding", tags=["Embedding"])


@router.get("/search", response_model=dict)
async def search_by_embedding(
    query: str = Query(..., description="Query text for semantic search", min_length=1, max_length=1000),
    top_k: int = Query(default=5, description="Number of results to return", ge=1, le=20),
):
    """
    Semantic search using text embedding

    This endpoint:
    1. Converts the query text to an embedding vector using Bailian text-embedding-v4
    2. Searches the vector database for similar medical information
    3. Returns the most relevant results

    - **query**: The query text to search for
    - **top_k**: Number of results to return (default: 5, max: 20)
    """
    try:
        # Execute vector search (includes embedding and retrieval)
        results = await vector_search_service.search(
            query=query,
            limit=top_k,
        )

        return {
            "query": query,
            "total_matches": len(results),
            "results": results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embed", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    """
    Create embedding vector from text

    This endpoint converts the input text to an embedding vector using
    Bailian text-embedding-v4 model.

    - **text**: The text to convert to embedding
    """
    try:
        embedding = await embedding_service.embed_text(request.text)

        return EmbeddingResponse(
            text=request.text,
            embedding=embedding,
            dimension=len(embedding),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/embed", response_model=EmbeddingResponse)
async def create_embedding_get(
    text: str = Query(..., description="Text to convert to embedding", min_length=1, max_length=2048),
):
    """
    Create embedding vector from text (GET method)

    This endpoint converts the input text to an embedding vector using
    Bailian text-embedding-v4 model.

    - **text**: The text to convert to embedding
    """
    try:
        embedding = await embedding_service.embed_text(text)

        return EmbeddingResponse(
            text=text,
            embedding=embedding,
            dimension=len(embedding),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Embedding service health check"""
    try:
        # Try to initialize service to check if configuration is correct
        from app.services.embedding_service import EmbeddingService

        EmbeddingService()
        return {"status": "healthy", "service": "bailian-embedding"}
    except Exception as e:
        return {"status": "unhealthy", "service": "bailian-embedding", "error": str(e)}


@router.post("/store", response_model=StoreResponse)
async def store_embedding(request: StoreRequest):
    """
    Store text embedding in Qdrant vector database

    This endpoint:
    1. Converts the input text to an embedding vector using Bailian text-embedding-v4
    2. Stores the vector and original text in Qdrant
    3. Returns the point ID and embedding info

    - **text**: The text to embed and store
    - **metadata**: Optional metadata to store with the text
    """
    try:
        # Generate embedding
        embedding = await embedding_service.embed_text(request.text)

        # Prepare payload with original text and optional metadata
        payload = {"text": request.text}
        if request.metadata:
            payload.update(request.metadata)

        # Store in Qdrant
        point_id = qdrant_client.upsert_point(vector=embedding, payload=payload)

        return StoreResponse(
            point_id=point_id,
            text=request.text,
            dimension=len(embedding),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
