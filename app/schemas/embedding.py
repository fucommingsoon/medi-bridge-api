"""Embedding Related Data Models"""
from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):
    """Embedding request"""

    text: str = Field(..., description="Text to embed", min_length=1, max_length=2048)


class EmbeddingResponse(BaseModel):
    """Embedding response"""

    text: str = Field(..., description="Original text")
    embedding: list[float] = Field(..., description="Embedding vector")
    dimension: int = Field(..., description="Vector dimension")


class SearchRequest(BaseModel):
    """Search request via POST"""

    query: str = Field(..., description="Query text", min_length=1, max_length=1000)
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)
