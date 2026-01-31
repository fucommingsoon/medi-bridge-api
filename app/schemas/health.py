"""Health Check Response"""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    service: str
    version: str
    qdrant_connected: bool
