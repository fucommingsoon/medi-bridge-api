"""API v1 Router Aggregation"""
from fastapi import APIRouter

from app.api.v1 import consultation, asr, embedding, sqlite

api_router = APIRouter()

# Register module routes
api_router.include_router(consultation.router)
api_router.include_router(asr.router)
api_router.include_router(embedding.router)
api_router.include_router(sqlite.router)
