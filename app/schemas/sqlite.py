"""Pydantic Schemas for SQLite Database Models

This module defines request and response schemas for SQLite database entities.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# Common Schemas
# ============================================================================


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""

    created_at: datetime = Field(description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")


# ============================================================================
# Disease Schemas
# ============================================================================


class DiseaseBase(BaseModel):
    """Base disease schema"""

    cui: str = Field(..., max_length=50, description="Disease CUI (unique identifier)")
    name: str = Field(..., max_length=500, description="Disease name")
    alias: Optional[str] = Field(None, description="Disease aliases (pipe-separated)")
    definition: Optional[str] = Field(None, description="Disease definition")
    external_ids: Optional[str] = Field(None, description="External IDs (pipe-separated)")


class DiseaseCreate(DiseaseBase):
    """Schema for creating a disease"""

    pass


class DiseaseUpdate(BaseModel):
    """Schema for updating a disease"""

    name: Optional[str] = Field(None, max_length=500, description="Disease name")
    alias: Optional[str] = Field(None, description="Disease aliases (pipe-separated)")
    definition: Optional[str] = Field(None, description="Disease definition")
    external_ids: Optional[str] = Field(None, description="External IDs (pipe-separated)")


class DiseaseResponse(DiseaseBase, TimestampMixin):
    """Schema for disease response"""

    id: int = Field(description="Disease ID")

    class Config:
        from_attributes = True


class DiseaseListResponse(BaseModel):
    """Schema for disease list response"""

    total: int = Field(description="Total number of diseases")
    items: list[DiseaseResponse] = Field(description="List of diseases")


# ============================================================================
# Symptom Schemas
# ============================================================================


class SymptomBase(BaseModel):
    """Base symptom schema"""

    cui: str = Field(..., max_length=50, description="Symptom CUI (unique identifier)")
    name: str = Field(..., max_length=500, description="Symptom name")
    alias: Optional[str] = Field(None, description="Symptom aliases (pipe-separated)")
    definition: Optional[str] = Field(None, description="Symptom definition")
    external_ids: Optional[str] = Field(None, description="External IDs (pipe-separated)")


class SymptomCreate(SymptomBase):
    """Schema for creating a symptom"""

    full_description: Optional[str] = Field(None, description="Complete symptom information")
    summary: Optional[str] = Field(None, description="Symptom summary")


class SymptomUpdate(BaseModel):
    """Schema for updating a symptom"""

    name: Optional[str] = Field(None, max_length=500, description="Symptom name")
    alias: Optional[str] = Field(None, description="Symptom aliases (pipe-separated)")
    definition: Optional[str] = Field(None, description="Symptom definition")
    external_ids: Optional[str] = Field(None, description="External IDs (pipe-separated)")
    full_description: Optional[str] = Field(None, description="Complete symptom information")
    summary: Optional[str] = Field(None, description="Symptom summary")


class SymptomResponse(SymptomBase, TimestampMixin):
    """Schema for symptom response"""

    id: int = Field(description="Symptom ID")
    full_description: Optional[str] = Field(None, description="Complete symptom information")
    summary: Optional[str] = Field(None, description="Symptom summary")

    class Config:
        from_attributes = True


class SymptomListResponse(BaseModel):
    """Schema for symptom list response"""

    total: int = Field(description="Total number of symptoms")
    items: list[SymptomResponse] = Field(description="List of symptoms")


# ============================================================================
# Disease-Symptom Association Schemas
# ============================================================================


class DiseaseSymptomAssociationCreate(BaseModel):
    """Schema for creating a disease-symptom association"""

    disease_id: int = Field(..., description="Disease ID")
    symptom_id: int = Field(..., description="Symptom ID")
    source: Optional[str] = Field(None, max_length=200, description="Data source")


class DiseaseSymptomAssociationResponse(BaseModel):
    """Schema for disease-symptom association response"""

    id: int = Field(description="Association ID")
    disease_id: int = Field(description="Disease ID")
    symptom_id: int = Field(description="Symptom ID")
    source: Optional[str] = Field(None, description="Data source")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# Extended Response Schemas with Relationships
# ============================================================================


class DiseaseWithSymptomsResponse(DiseaseResponse):
    """Schema for disease response with associated symptoms"""

    symptoms: list[SymptomResponse] = Field(
        default_factory=list, description="Associated symptoms"
    )


class SymptomWithDiseasesResponse(SymptomResponse):
    """Schema for symptom response with associated diseases"""

    diseases: list[DiseaseResponse] = Field(
        default_factory=list, description="Associated diseases"
    )


# ============================================================================
# Conversation Schemas
# ============================================================================


class ConversationBase(BaseModel):
    """Base conversation schema"""

    title: str = Field(..., min_length=1, max_length=255, description="Conversation title")
    started_at: datetime = Field(description="Session start time")
    department: Optional[str] = Field(None, max_length=100, description="Department/Category")
    patient_id: Optional[int] = Field(None, description="Patient ID (reserved)")
    progress: Optional[str] = Field(None, description="Current progress (JSON array)")


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""

    user_id: Optional[int] = Field(None, description="Current logged-in user ID (reserved)")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Conversation title")
    department: Optional[str] = Field(None, max_length=100, description="Department/Category")
    patient_id: Optional[int] = Field(None, description="Patient ID")
    progress: Optional[str] = Field(None, description="Current progress")
    user_id: Optional[int] = Field(None, description="Current logged-in user ID")


class ConversationResponse(ConversationBase, TimestampMixin):
    """Schema for conversation response"""

    id: int = Field(description="Conversation ID")
    user_id: Optional[int] = Field(None, description="Current logged-in user ID")

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schema for conversation list response"""

    total: int = Field(description="Total number of conversations")
    items: list[ConversationResponse] = Field(description="List of conversations")


class ConversationWithMessagesResponse(ConversationResponse):
    """Schema for conversation response with messages"""

    messages: list["MessageResponse"] = Field(
        default_factory=list, description="Messages in this conversation"
    )


# ============================================================================
# Message Schemas
# ============================================================================


class MessageBase(BaseModel):
    """Base message schema"""

    content: str = Field(..., min_length=1, description="Message content (text)")


class MessageCreate(MessageBase):
    """Schema for creating a message"""

    conversation_id: int = Field(..., description="Conversation ID")
    role: Optional[str] = Field(None, max_length=50, description="Message role (reserved)")


class MessageUpdate(BaseModel):
    """Schema for updating a message"""

    content: Optional[str] = Field(None, min_length=1, description="Message content")
    role: Optional[str] = Field(None, max_length=50, description="Message role")


class MessageResponse(MessageBase):
    """Schema for message response"""

    id: int = Field(description="Message ID")
    conversation_id: int = Field(description="Conversation ID")
    sent_at: datetime = Field(description="Message send time")
    role: Optional[str] = Field(None, description="Message role")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for message list response"""

    total: int = Field(description="Total number of messages")
    items: list[MessageResponse] = Field(description="List of messages")
