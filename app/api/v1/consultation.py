"""Consultation API Routes"""
from fastapi import APIRouter, HTTPException

from app.schemas.consultation import ConsultationRequest, ConsultationResponse
from app.services.vector_search import vector_search_service

router = APIRouter(prefix="/consultation", tags=["Consultation"])


@router.post("/query", response_model=ConsultationResponse)
async def query_symptoms(request: ConsultationRequest) -> ConsultationResponse:
    """
    Query relevant medical information based on user description

    Args:
        request: Request body containing user query

    Returns:
        List of matched medical information
    """
    try:
        # TODO: Implement query vectorization
        query_vector: list[float] = []

        # Execute vector search
        results = await vector_search_service.search(
            query_vector=query_vector,
            limit=request.top_k,
        )

        return ConsultationResponse(
            query=request.query,
            results=[],
            total_matches=len(results),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Vector database health check"""
    is_healthy = await vector_search_service.health_check()
    return {"status": "healthy" if is_healthy else "unhealthy"}
