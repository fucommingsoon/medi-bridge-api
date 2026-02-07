"""Pydantic Schemas for SQLite Database Models

This module defines request and response schemas for the SQLite database entities.
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
# Condition Schemas
# ============================================================================


class ConditionBase(BaseModel):
    """Base condition schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Condition name")
    full_description: str = Field(..., min_length=1, description="Complete condition information")
    summary: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Condition summary for Qdrant (max 1000 chars)",
    )


class ConditionCreate(ConditionBase):
    """Schema for creating a condition"""

    pass


class ConditionUpdate(BaseModel):
    """Schema for updating a condition"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Condition name")
    full_description: Optional[str] = Field(None, min_length=1, description="Complete condition information")
    summary: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1000,
        description="Condition summary for Qdrant (max 1000 chars)",
    )


class ConditionResponse(ConditionBase, TimestampMixin):
    """Schema for condition response"""

    id: int = Field(description="Condition ID")

    class Config:
        from_attributes = True


class ConditionListResponse(BaseModel):
    """Schema for condition list response"""

    total: int = Field(description="Total number of conditions")
    items: list[ConditionResponse] = Field(description="List of conditions")


# ============================================================================
# Exclusion Method Schemas
# ============================================================================


class ExclusionMethodBase(BaseModel):
    """Base exclusion method schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Method name")
    description: str = Field(..., min_length=1, description="Method description")
    procedure_steps: Optional[str] = Field(None, description="JSON array of procedure steps")


class ExclusionMethodCreate(ExclusionMethodBase):
    """Schema for creating an exclusion method"""

    pass


class ExclusionMethodUpdate(BaseModel):
    """Schema for updating an exclusion method"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Method name")
    description: Optional[str] = Field(None, min_length=1, description="Method description")
    procedure_steps: Optional[str] = Field(None, description="JSON array of procedure steps")


class ExclusionMethodResponse(ExclusionMethodBase, TimestampMixin):
    """Schema for exclusion method response"""

    id: int = Field(description="Exclusion method ID")

    class Config:
        from_attributes = True


class ExclusionMethodListResponse(BaseModel):
    """Schema for exclusion method list response"""

    total: int = Field(description="Total number of exclusion methods")
    items: list[ExclusionMethodResponse] = Field(description="List of exclusion methods")


# ============================================================================
# Treatment Plan Schemas
# ============================================================================


class TreatmentPlanBase(BaseModel):
    """Base treatment plan schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Plan name")
    description: str = Field(..., min_length=1, description="Plan description")
    medications: Optional[str] = Field(None, description="JSON array of medications")
    procedures: Optional[str] = Field(None, description="JSON array of procedures")
    factors: Optional[str] = Field(None, description="JSON array of influencing factors")
    contraindications: Optional[str] = Field(
        None, description="JSON array of contraindications"
    )


class TreatmentPlanCreate(TreatmentPlanBase):
    """Schema for creating a treatment plan"""

    pass


class TreatmentPlanUpdate(BaseModel):
    """Schema for updating a treatment plan"""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Plan name")
    description: Optional[str] = Field(None, min_length=1, description="Plan description")
    medications: Optional[str] = Field(None, description="JSON array of medications")
    procedures: Optional[str] = Field(None, description="JSON array of procedures")
    factors: Optional[str] = Field(None, description="JSON array of influencing factors")
    contraindications: Optional[str] = Field(
        None, description="JSON array of contraindications"
    )


class TreatmentPlanResponse(TreatmentPlanBase, TimestampMixin):
    """Schema for treatment plan response"""

    id: int = Field(description="Treatment plan ID")

    class Config:
        from_attributes = True


class TreatmentPlanListResponse(BaseModel):
    """Schema for treatment plan list response"""

    total: int = Field(description="Total number of treatment plans")
    items: list[TreatmentPlanResponse] = Field(description="List of treatment plans")


# ============================================================================
# Association Schemas
# ============================================================================


class ConditionExclusionMethodCreate(BaseModel):
    """Schema for associating a condition with an exclusion method"""

    condition_id: int = Field(..., description="Condition ID")
    exclusion_method_id: int = Field(..., description="Exclusion method ID")


class ConditionExclusionMethodResponse(BaseModel):
    """Schema for condition-exclusion method association response"""

    id: int = Field(description="Association ID")
    condition_id: int = Field(description="Condition ID")
    exclusion_method_id: int = Field(description="Exclusion method ID")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


class ConditionTreatmentPlanCreate(BaseModel):
    """Schema for associating a condition with a treatment plan"""

    condition_id: int = Field(..., description="Condition ID")
    treatment_plan_id: int = Field(..., description="Treatment plan ID")
    is_primary: bool = Field(False, description="Whether this is the primary plan")
    priority: int = Field(0, description="Priority ordering (higher = more important)")
    notes: Optional[str] = Field(None, description="Additional notes for this association")


class ConditionTreatmentPlanUpdate(BaseModel):
    """Schema for updating a condition-treatment plan association"""

    is_primary: Optional[bool] = Field(None, description="Whether this is the primary plan")
    priority: Optional[int] = Field(None, description="Priority ordering (higher = more important)")
    notes: Optional[str] = Field(None, description="Additional notes for this association")


class ConditionTreatmentPlanResponse(BaseModel):
    """Schema for condition-treatment plan association response"""

    id: int = Field(description="Association ID")
    condition_id: int = Field(description="Condition ID")
    treatment_plan_id: int = Field(description="Treatment plan ID")
    is_primary: bool = Field(description="Whether this is the primary plan")
    priority: int = Field(description="Priority ordering (higher = more important)")
    notes: Optional[str] = Field(None, description="Additional notes for this association")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


# ============================================================================
# Extended Response Schemas with Relationships
# ============================================================================


class ConditionWithRelationshipsResponse(ConditionResponse):
    """Schema for condition response with relationships"""

    exclusion_methods: list[ExclusionMethodResponse] = Field(
        default_factory=list, description="Associated exclusion methods"
    )
    treatment_plans: list[TreatmentPlanResponse] = Field(
        default_factory=list, description="Associated treatment plans"
    )


class TreatmentPlanWithConditionsResponse(TreatmentPlanResponse):
    """Schema for treatment plan response with associated conditions"""

    conditions: list[ConditionResponse] = Field(
        default_factory=list, description="Associated conditions"
    )


# ============================================================================
# Conversation Schemas
# ============================================================================


class ConversationBase(BaseModel):
    """Base conversation schema"""

    title: str = Field(..., min_length=1, max_length=255, description="Conversation title")
    department: Optional[str] = Field(None, max_length=100, description="Department/Category")
    progress: Optional[str] = Field(None, description="Current progress (JSON array of condition IDs)")


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""

    user_id: Optional[int] = Field(None, description="Current logged-in user ID (reserved)")
    patient_id: Optional[int] = Field(None, description="Patient ID (reserved)")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Conversation title")
    department: Optional[str] = Field(None, max_length=100, description="Department/Category")
    progress: Optional[str] = Field(None, description="Current progress (JSON array of condition IDs)")
    user_id: Optional[int] = Field(None, description="Current logged-in user ID (reserved)")
    patient_id: Optional[int] = Field(None, description="Patient ID (reserved)")


class ConversationResponse(ConversationBase, TimestampMixin):
    """Schema for conversation response"""

    id: int = Field(description="Conversation ID")
    user_id: Optional[int] = Field(None, description="Current logged-in user ID (reserved)")
    patient_id: Optional[int] = Field(None, description="Patient ID (reserved)")
    started_at: datetime = Field(description="Session start time")

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

    content: Optional[str] = Field(None, min_length=1, description="Message content (text)")
    role: Optional[str] = Field(None, max_length=50, description="Message role (reserved)")


class MessageResponse(MessageBase):
    """Schema for message response"""

    id: int = Field(description="Message ID")
    conversation_id: int = Field(description="Conversation ID")
    sent_at: datetime = Field(description="Message send time")
    role: Optional[str] = Field(None, description="Message role (reserved)")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for message list response"""

    total: int = Field(description="Total number of messages")
    items: list[MessageResponse] = Field(description="List of messages")


# Update forward references
ConversationWithMessagesResponse.model_rebuild()
