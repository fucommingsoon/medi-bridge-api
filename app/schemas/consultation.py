"""Consultation Related Data Models"""
from pydantic import BaseModel, Field


class ConsultationRequest(BaseModel):
    """Consultation request"""

    query: str = Field(..., description="User-described symptoms or questions", min_length=1, max_length=1000)
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=20)


class SymptomInfo(BaseModel):
    """Symptom information"""

    symptom_name: str = Field(..., description="Symptom name")
    description: str = Field(..., description="Symptom description")
    possible_diseases: list[str] = Field(default_factory=list, description="Possible related diseases")
    confidence_score: float = Field(..., description="Confidence score", ge=0, le=1)


class ConsultationResponse(BaseModel):
    """Consultation response"""

    query: str = Field(..., description="Original query")
    results: list[SymptomInfo] = Field(default_factory=list, description="Matched symptom information")
    total_matches: int = Field(default=0, description="Total number of matched results")
