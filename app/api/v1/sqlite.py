"""SQLite Database API Endpoints

This module provides REST API endpoints for managing SQLite database entities.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.sqlite_db import SQLiteClientWrapper
from app.schemas.sqlite import (
    ConditionCreate,
    ConditionExclusionMethodCreate,
    ConditionExclusionMethodResponse,
    ConditionListResponse,
    ConditionResponse,
    ConditionTreatmentPlanCreate,
    ConditionTreatmentPlanResponse,
    ConditionTreatmentPlanUpdate,
    ConditionUpdate,
    ConditionWithRelationshipsResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessagesResponse,
    ExclusionMethodCreate,
    ExclusionMethodListResponse,
    ExclusionMethodResponse,
    ExclusionMethodUpdate,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    MessageUpdate,
    SympganDiseaseCreate,
    SympganDiseaseListResponse,
    SympganDiseaseResponse,
    SympganDiseaseSymptomAssociationCreate,
    SympganDiseaseSymptomAssociationResponse,
    SympganDiseaseUpdate,
    SympganDiseaseWithSymptomsResponse,
    SympganSymptomCreate,
    SympganSymptomListResponse,
    SympganSymptomResponse,
    SympganSymptomUpdate,
    SympganSymptomWithDiseasesResponse,
    TreatmentPlanCreate,
    TreatmentPlanListResponse,
    TreatmentPlanResponse,
    TreatmentPlanUpdate,
)
from app.services.sqlite_crud import (
    ConditionExclusionMethodService,
    ConditionService,
    ConditionTreatmentPlanService,
    ConversationService,
    ExclusionMethodService,
    MessageService,
    SympganDiseaseService,
    SympganDiseaseSymptomAssociationService,
    SympganSymptomService,
    TreatmentPlanService,
)

router = APIRouter(prefix="/sqlite", tags=["SQLite Database"])


# ============================================================================
# Dependencies
# ============================================================================


async def get_db_session():
    """Dependency for getting database session"""
    async with await SQLiteClientWrapper.get_session() as session:
        yield session


SessionDep = Annotated[object, Depends(get_db_session)]


# ============================================================================
# Condition Endpoints
# ============================================================================


@router.post("/conditions", response_model=ConditionResponse, status_code=status.HTTP_201_CREATED)
async def create_condition(session: SessionDep, data: ConditionCreate):
    """Create a new medical condition

    Args:
        session: Database session
        data: Condition creation data

    Returns:
        Created condition
    """
    condition = await ConditionService.create(session, data.model_dump())
    return condition


@router.get("/conditions/{condition_id}", response_model=ConditionWithRelationshipsResponse)
async def get_condition(condition_id: int, session: SessionDep):
    """Get a condition by ID with relationships

    Args:
        condition_id: Condition ID
        session: Database session

    Returns:
        Condition with relationships

    Raises:
        HTTPException: If condition not found
    """
    condition = await ConditionService.get_with_relationships(session, condition_id)
    if not condition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")

    # Build exclusion methods list
    exclusion_methods = [
        ExclusionMethodResponse(
            id=assoc.exclusion_method.id,
            name=assoc.exclusion_method.name,
            description=assoc.exclusion_method.description,
            procedure_steps=assoc.exclusion_method.procedure_steps,
            created_at=assoc.exclusion_method.created_at,
            updated_at=assoc.exclusion_method.updated_at,
        )
        for assoc in condition.exclusion_methods
    ]

    # Build treatment plans list
    treatment_plans = [
        TreatmentPlanResponse(
            id=assoc.treatment_plan.id,
            name=assoc.treatment_plan.name,
            description=assoc.treatment_plan.description,
            medications=assoc.treatment_plan.medications,
            procedures=assoc.treatment_plan.procedures,
            factors=assoc.treatment_plan.factors,
            contraindications=assoc.treatment_plan.contraindications,
            created_at=assoc.treatment_plan.created_at,
            updated_at=assoc.treatment_plan.updated_at,
        )
        for assoc in condition.treatment_plans
    ]

    return ConditionWithRelationshipsResponse(
        id=condition.id,
        name=condition.name,
        full_description=condition.full_description,
        summary=condition.summary,
        created_at=condition.created_at,
        updated_at=condition.updated_at,
        exclusion_methods=exclusion_methods,
        treatment_plans=treatment_plans,
    )


@router.get("/conditions", response_model=ConditionListResponse)
async def list_conditions(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all conditions with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of conditions
    """
    total, conditions = await ConditionService.list(session, skip=skip, limit=limit)

    return ConditionListResponse(
        total=total,
        items=[
            ConditionResponse(
                id=c.id,
                name=c.name,
                full_description=c.full_description,
                summary=c.summary,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conditions
        ],
    )


@router.patch("/conditions/{condition_id}", response_model=ConditionResponse)
async def update_condition(condition_id: int, session: SessionDep, data: ConditionUpdate):
    """Update a condition

    Args:
        condition_id: Condition ID
        session: Database session
        data: Update data

    Returns:
        Updated condition

    Raises:
        HTTPException: If condition not found
    """
    condition = await ConditionService.update(session, condition_id, data)
    if not condition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")

    return ConditionResponse(
        id=condition.id,
        name=condition.name,
        full_description=condition.full_description,
        summary=condition.summary,
        created_at=condition.created_at,
        updated_at=condition.updated_at,
    )


@router.delete("/conditions/{condition_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_condition(condition_id: int, session: SessionDep):
    """Delete a condition

    Args:
        condition_id: Condition ID
        session: Database session

    Raises:
        HTTPException: If condition not found
    """
    deleted = await ConditionService.delete(session, condition_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Condition not found")


# ============================================================================
# Exclusion Method Endpoints
# ============================================================================


@router.post(
    "/exclusion-methods",
    response_model=ExclusionMethodResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exclusion_method(session: SessionDep, data: ExclusionMethodCreate):
    """Create a new exclusion method

    Args:
        session: Database session
        data: Exclusion method creation data

    Returns:
        Created exclusion method
    """
    method = await ExclusionMethodService.create(session, data.model_dump())
    return method


@router.get("/exclusion-methods/{method_id}", response_model=ExclusionMethodResponse)
async def get_exclusion_method(method_id: int, session: SessionDep):
    """Get an exclusion method by ID

    Args:
        method_id: Exclusion method ID
        session: Database session

    Returns:
        Exclusion method

    Raises:
        HTTPException: If exclusion method not found
    """
    method = await ExclusionMethodService.get(session, method_id)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion method not found"
        )

    return ExclusionMethodResponse(
        id=method.id,
        name=method.name,
        description=method.description,
        procedure_steps=method.procedure_steps,
        created_at=method.created_at,
        updated_at=method.updated_at,
    )


@router.get("/exclusion-methods", response_model=ExclusionMethodListResponse)
async def list_exclusion_methods(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all exclusion methods with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of exclusion methods
    """
    total, methods = await ExclusionMethodService.list(session, skip=skip, limit=limit)

    return ExclusionMethodListResponse(
        total=total,
        items=[
            ExclusionMethodResponse(
                id=m.id,
                name=m.name,
                description=m.description,
                procedure_steps=m.procedure_steps,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in methods
        ],
    )


@router.patch("/exclusion-methods/{method_id}", response_model=ExclusionMethodResponse)
async def update_exclusion_method(method_id: int, session: SessionDep, data: ExclusionMethodUpdate):
    """Update an exclusion method

    Args:
        method_id: Exclusion method ID
        session: Database session
        data: Update data

    Returns:
        Updated exclusion method

    Raises:
        HTTPException: If exclusion method not found
    """
    method = await ExclusionMethodService.update(session, method_id, data)
    if not method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion method not found"
        )

    return ExclusionMethodResponse(
        id=method.id,
        name=method.name,
        description=method.description,
        procedure_steps=method.procedure_steps,
        created_at=method.created_at,
        updated_at=method.updated_at,
    )


@router.delete("/exclusion-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exclusion_method(method_id: int, session: SessionDep):
    """Delete an exclusion method

    Args:
        method_id: Exclusion method ID
        session: Database session

    Raises:
        HTTPException: If exclusion method not found
    """
    deleted = await ExclusionMethodService.delete(session, method_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Exclusion method not found"
        )


# ============================================================================
# Treatment Plan Endpoints
# ============================================================================


@router.post("/treatment-plans", response_model=TreatmentPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment_plan(session: SessionDep, data: TreatmentPlanCreate):
    """Create a new treatment plan

    Args:
        session: Database session
        data: Treatment plan creation data

    Returns:
        Created treatment plan
    """
    plan = await TreatmentPlanService.create(session, data.model_dump())
    return plan


@router.get("/treatment-plans/{plan_id}", response_model=TreatmentPlanResponse)
async def get_treatment_plan(plan_id: int, session: SessionDep):
    """Get a treatment plan by ID

    Args:
        plan_id: Treatment plan ID
        session: Database session

    Returns:
        Treatment plan

    Raises:
        HTTPException: If treatment plan not found
    """
    plan = await TreatmentPlanService.get(session, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment plan not found")

    return TreatmentPlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        medications=plan.medications,
        procedures=plan.procedures,
        factors=plan.factors,
        contraindications=plan.contraindications,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.get("/treatment-plans", response_model=TreatmentPlanListResponse)
async def list_treatment_plans(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all treatment plans with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of treatment plans
    """
    total, plans = await TreatmentPlanService.list(session, skip=skip, limit=limit)

    return TreatmentPlanListResponse(
        total=total,
        items=[
            TreatmentPlanResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                medications=p.medications,
                procedures=p.procedures,
                factors=p.factors,
                contraindications=p.contraindications,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in plans
        ],
    )


@router.patch("/treatment-plans/{plan_id}", response_model=TreatmentPlanResponse)
async def update_treatment_plan(plan_id: int, session: SessionDep, data: TreatmentPlanUpdate):
    """Update a treatment plan

    Args:
        plan_id: Treatment plan ID
        session: Database session
        data: Update data

    Returns:
        Updated treatment plan

    Raises:
        HTTPException: If treatment plan not found
    """
    plan = await TreatmentPlanService.update(session, plan_id, data)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment plan not found")

    return TreatmentPlanResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        medications=plan.medications,
        procedures=plan.procedures,
        factors=plan.factors,
        contraindications=plan.contraindications,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.delete("/treatment-plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_treatment_plan(plan_id: int, session: SessionDep):
    """Delete a treatment plan

    Args:
        plan_id: Treatment plan ID
        session: Database session

    Raises:
        HTTPException: If treatment plan not found
    """
    deleted = await TreatmentPlanService.delete(session, plan_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment plan not found")


# ============================================================================
# Association Management Endpoints
# ============================================================================


@router.post(
    "/conditions/{condition_id}/exclusion-methods",
    response_model=ConditionExclusionMethodResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_condition_exclusion_method(
    condition_id: int, session: SessionDep, data: ConditionExclusionMethodCreate
):
    """Associate an exclusion method with a condition

    Args:
        condition_id: Condition ID
        session: Database session
        data: Association data

    Returns:
        Created association
    """
    # Override condition_id from path
    data_dict = data.model_dump()
    data_dict["condition_id"] = condition_id

    association = await ConditionExclusionMethodService.add_association(
        session, ConditionExclusionMethodCreate(**data_dict)
    )
    return association


@router.delete(
    "/condition-exclusion-methods/{association_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_condition_exclusion_method(association_id: int, session: SessionDep):
    """Remove a condition-exclusion method association

    Args:
        association_id: Association ID
        session: Database session

    Raises:
        HTTPException: If association not found
    """
    deleted = await ConditionExclusionMethodService.remove_association(session, association_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Association not found"
        )


@router.get("/conditions/{condition_id}/exclusion-methods", response_model=ExclusionMethodListResponse)
async def get_condition_exclusion_methods(condition_id: int, session: SessionDep):
    """Get all exclusion methods for a condition

    Args:
        condition_id: Condition ID
        session: Database session

    Returns:
        List of exclusion methods
    """
    methods = await ConditionExclusionMethodService.get_condition_exclusion_methods(
        session, condition_id
    )

    return ExclusionMethodListResponse(
        total=len(methods),
        items=[
            ExclusionMethodResponse(
                id=m.id,
                name=m.name,
                description=m.description,
                procedure_steps=m.procedure_steps,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in methods
        ],
    )


@router.post(
    "/conditions/{condition_id}/treatment-plans",
    response_model=ConditionTreatmentPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_condition_treatment_plan(
    condition_id: int, session: SessionDep, data: ConditionTreatmentPlanCreate
):
    """Associate a treatment plan with a condition

    Args:
        condition_id: Condition ID
        session: Database session
        data: Association data

    Returns:
        Created association
    """
    # Override condition_id from path
    data_dict = data.model_dump()
    data_dict["condition_id"] = condition_id

    association = await ConditionTreatmentPlanService.add_association(
        session, ConditionTreatmentPlanCreate(**data_dict)
    )
    return association


@router.patch(
    "/condition-treatment-plans/{association_id}",
    response_model=ConditionTreatmentPlanResponse,
)
async def update_condition_treatment_plan(
    association_id: int, session: SessionDep, data: ConditionTreatmentPlanUpdate
):
    """Update a condition-treatment plan association

    Args:
        association_id: Association ID
        session: Database session
        data: Update data

    Returns:
        Updated association

    Raises:
        HTTPException: If association not found
    """
    association = await ConditionTreatmentPlanService.update_association(
        session, association_id, data
    )
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Association not found"
        )

    return ConditionTreatmentPlanResponse(
        id=association.id,
        condition_id=association.condition_id,
        treatment_plan_id=association.treatment_plan_id,
        is_primary=association.is_primary,
        priority=association.priority,
        notes=association.notes,
        created_at=association.created_at,
    )


@router.delete(
    "/condition-treatment-plans/{association_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_condition_treatment_plan(association_id: int, session: SessionDep):
    """Remove a condition-treatment plan association

    Args:
        association_id: Association ID
        session: Database session

    Raises:
        HTTPException: If association not found
    """
    deleted = await ConditionTreatmentPlanService.remove_association(session, association_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Association not found"
        )


@router.get("/conditions/{condition_id}/treatment-plans", response_model=TreatmentPlanListResponse)
async def get_condition_treatment_plans(condition_id: int, session: SessionDep):
    """Get all treatment plans for a condition

    Args:
        condition_id: Condition ID
        session: Database session

    Returns:
        List of treatment plans
    """
    plans = await ConditionTreatmentPlanService.get_condition_treatment_plans(
        session, condition_id
    )

    return TreatmentPlanListResponse(
        total=len(plans),
        items=[
            TreatmentPlanResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                medications=p.medications,
                procedures=p.procedures,
                factors=p.factors,
                contraindications=p.contraindications,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in plans
        ],
    )


# ============================================================================
# Conversation Endpoints
# ============================================================================


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(session: SessionDep, data: ConversationCreate):
    """Create a new conversation

    Args:
        session: Database session
        data: Conversation creation data

    Returns:
        Created conversation
    """
    conversation = await ConversationService.create(session, data.model_dump())
    return conversation


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(conversation_id: int, session: SessionDep):
    """Get a conversation by ID with messages

    Args:
        conversation_id: Conversation ID
        session: Database session

    Returns:
        Conversation with messages

    Raises:
        HTTPException: If conversation not found
    """
    conversation = await ConversationService.get_with_messages(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    # Build messages list
    messages = [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            content=m.content,
            sent_at=m.sent_at,
            role=m.role,
            created_at=m.created_at,
        )
        for m in conversation.messages
    ]

    return ConversationWithMessagesResponse(
        id=conversation.id,
        title=conversation.title,
        department=conversation.department,
        progress=conversation.progress,
        user_id=conversation.user_id,
        patient_id=conversation.patient_id,
        started_at=conversation.started_at,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=messages,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all conversations with pagination (most recent first)

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of conversations
    """
    total, conversations = await ConversationService.list(session, skip=skip, limit=limit)

    return ConversationListResponse(
        total=total,
        items=[
            ConversationResponse(
                id=c.id,
                title=c.title,
                department=c.department,
                progress=c.progress,
                user_id=c.user_id,
                patient_id=c.patient_id,
                started_at=c.started_at,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
        ],
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(conversation_id: int, session: SessionDep, data: ConversationUpdate):
    """Update a conversation

    Args:
        conversation_id: Conversation ID
        session: Database session
        data: Update data

    Returns:
        Updated conversation

    Raises:
        HTTPException: If conversation not found
    """
    conversation = await ConversationService.update(session, conversation_id, data)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        department=conversation.department,
        progress=conversation.progress,
        user_id=conversation.user_id,
        patient_id=conversation.patient_id,
        started_at=conversation.started_at,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: int, session: SessionDep):
    """Delete a conversation (and all associated messages)

    Args:
        conversation_id: Conversation ID
        session: Database session

    Raises:
        HTTPException: If conversation not found
    """
    deleted = await ConversationService.delete(session, conversation_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


# ============================================================================
# Message Endpoints
# ============================================================================


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(session: SessionDep, data: MessageCreate):
    """Create a new message

    Args:
        session: Database session
        data: Message creation data

    Returns:
        Created message
    """
    message = await MessageService.create(session, data.model_dump())
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        content=message.content,
        sent_at=message.sent_at,
        role=message.role,
        created_at=message.created_at,
    )


@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(message_id: int, session: SessionDep):
    """Get a message by ID

    Args:
        message_id: Message ID
        session: Database session

    Returns:
        Message

    Raises:
        HTTPException: If message not found
    """
    message = await MessageService.get(session, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        content=message.content,
        sent_at=message.sent_at,
        role=message.role,
        created_at=message.created_at,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def list_conversation_messages(
    conversation_id: int,
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all messages in a conversation (oldest first for chat history)

    Args:
        conversation_id: Conversation ID
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of messages
    """
    # Verify conversation exists
    conversation = await ConversationService.get(session, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    total, messages = await MessageService.list_by_conversation(
        session, conversation_id, skip=skip, limit=limit
    )

    return MessageListResponse(
        total=total,
        items=[
            MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                content=m.content,
                sent_at=m.sent_at,
                role=m.role,
                created_at=m.created_at,
            )
            for m in messages
        ],
    )


@router.patch("/messages/{message_id}", response_model=MessageResponse)
async def update_message(message_id: int, session: SessionDep, data: MessageUpdate):
    """Update a message

    Args:
        message_id: Message ID
        session: Database session
        data: Update data

    Returns:
        Updated message

    Raises:
        HTTPException: If message not found
    """
    message = await MessageService.update(session, message_id, data)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        content=message.content,
        sent_at=message.sent_at,
        role=message.role,
        created_at=message.created_at,
    )


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: int, session: SessionDep):
    """Delete a message

    Args:
        message_id: Message ID
        session: Database session

    Raises:
        HTTPException: If message not found
    """
    deleted = await MessageService.delete(session, message_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")


# ============================================================================
# SympGAN Disease Endpoints
# ============================================================================


@router.post("/sympgan-diseases", response_model=SympganDiseaseResponse, status_code=status.HTTP_201_CREATED)
async def create_sympgan_disease(session: SessionDep, data: SympganDiseaseCreate):
    """Create a new SympGAN disease

    Args:
        session: Database session
        data: Disease creation data

    Returns:
        Created disease
    """
    disease = await SympganDiseaseService.create(session, data.model_dump())
    return disease


@router.get("/sympgan-diseases/{disease_id}", response_model=SympganDiseaseWithSymptomsResponse)
async def get_sympgan_disease(disease_id: int, session: SessionDep):
    """Get a SympGAN disease by ID with symptoms

    Args:
        disease_id: Disease ID
        session: Database session

    Returns:
        Disease with symptoms

    Raises:
        HTTPException: If disease not found
    """
    disease = await SympganDiseaseService.get_with_symptoms(session, disease_id)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")

    # Build symptoms list
    symptoms = [
        SympganSymptomResponse(
            id=assoc.symptom.id,
            cui=assoc.symptom.cui,
            name=assoc.symptom.name,
            alias=assoc.symptom.alias,
            definition=assoc.symptom.definition,
            external_ids=assoc.symptom.external_ids,
            created_at=assoc.symptom.created_at,
            updated_at=assoc.symptom.updated_at,
        )
        for assoc in disease.symptom_associations
    ]

    return SympganDiseaseWithSymptomsResponse(
        id=disease.id,
        cui=disease.cui,
        name=disease.name,
        alias=disease.alias,
        definition=disease.definition,
        external_ids=disease.external_ids,
        created_at=disease.created_at,
        updated_at=disease.updated_at,
        symptoms=symptoms,
    )


@router.get("/sympgan-diseases", response_model=SympganDiseaseListResponse)
async def list_sympgan_diseases(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum records to return")] = 100,
):
    """List all SympGAN diseases with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of diseases
    """
    total, diseases = await SympganDiseaseService.list(session, skip=skip, limit=limit)

    return SympganDiseaseListResponse(
        total=total,
        items=[
            SympganDiseaseResponse(
                id=d.id,
                cui=d.cui,
                name=d.name,
                alias=d.alias,
                definition=d.definition,
                external_ids=d.external_ids,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in diseases
        ],
    )


@router.get("/sympgan-diseases/search/{query}", response_model=SympganDiseaseListResponse)
async def search_sympgan_diseases(
    query: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results to return")] = 10,
):
    """Search SympGAN diseases by name

    Args:
        query: Search query string
        session: Database session
        limit: Maximum results to return

    Returns:
        List of matching diseases
    """
    diseases = await SympganDiseaseService.search_by_name(session, query, limit)

    return SympganDiseaseListResponse(
        total=len(diseases),
        items=[
            SympganDiseaseResponse(
                id=d.id,
                cui=d.cui,
                name=d.name,
                alias=d.alias,
                definition=d.definition,
                external_ids=d.external_ids,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in diseases
        ],
    )


@router.patch("/sympgan-diseases/{disease_id}", response_model=SympganDiseaseResponse)
async def update_sympgan_disease(disease_id: int, session: SessionDep, data: SympganDiseaseUpdate):
    """Update a SympGAN disease

    Args:
        disease_id: Disease ID
        session: Database session
        data: Update data

    Returns:
        Updated disease

    Raises:
        HTTPException: If disease not found
    """
    disease = await SympganDiseaseService.update(session, disease_id, data)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")

    return SympganDiseaseResponse(
        id=disease.id,
        cui=disease.cui,
        name=disease.name,
        alias=disease.alias,
        definition=disease.definition,
        external_ids=disease.external_ids,
        created_at=disease.created_at,
        updated_at=disease.updated_at,
    )


@router.delete("/sympgan-diseases/{disease_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sympgan_disease(disease_id: int, session: SessionDep):
    """Delete a SympGAN disease (and all associated symptoms)

    Args:
        disease_id: Disease ID
        session: Database session

    Raises:
        HTTPException: If disease not found
    """
    deleted = await SympganDiseaseService.delete(session, disease_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")


# ============================================================================
# SympGAN Symptom Endpoints
# ============================================================================


@router.post("/sympgan-symptoms", response_model=SympganSymptomResponse, status_code=status.HTTP_201_CREATED)
async def create_sympgan_symptom(session: SessionDep, data: SympganSymptomCreate):
    """Create a new SympGAN symptom

    Args:
        session: Database session
        data: Symptom creation data

    Returns:
        Created symptom
    """
    symptom = await SympganSymptomService.create(session, data.model_dump())
    return symptom


@router.get("/sympgan-symptoms/{symptom_id}", response_model=SympganSymptomWithDiseasesResponse)
async def get_sympgan_symptom(symptom_id: int, session: SessionDep):
    """Get a SympGAN symptom by ID with diseases

    Args:
        symptom_id: Symptom ID
        session: Database session

    Returns:
        Symptom with diseases

    Raises:
        HTTPException: If symptom not found
    """
    symptom = await SympganSymptomService.get_with_diseases(session, symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")

    # Build diseases list
    diseases = [
        SympganDiseaseResponse(
            id=assoc.disease.id,
            cui=assoc.disease.cui,
            name=assoc.disease.name,
            alias=assoc.disease.alias,
            definition=assoc.disease.definition,
            external_ids=assoc.disease.external_ids,
            created_at=assoc.disease.created_at,
            updated_at=assoc.disease.updated_at,
        )
        for assoc in symptom.disease_associations
    ]

    return SympganSymptomWithDiseasesResponse(
        id=symptom.id,
        cui=symptom.cui,
        name=symptom.name,
        alias=symptom.alias,
        definition=symptom.definition,
        external_ids=symptom.external_ids,
        created_at=symptom.created_at,
        updated_at=symptom.updated_at,
        diseases=diseases,
    )


@router.get("/sympgan-symptoms", response_model=SympganSymptomListResponse)
async def list_sympgan_symptoms(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum records to return")] = 100,
):
    """List all SympGAN symptoms with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of symptoms
    """
    total, symptoms = await SympganSymptomService.list(session, skip=skip, limit=limit)

    return SympganSymptomListResponse(
        total=total,
        items=[
            SympganSymptomResponse(
                id=s.id,
                cui=s.cui,
                name=s.name,
                alias=s.alias,
                definition=s.definition,
                external_ids=s.external_ids,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in symptoms
        ],
    )


@router.get("/sympgan-symptoms/search/{query}", response_model=SympganSymptomListResponse)
async def search_sympgan_symptoms(
    query: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results to return")] = 10,
):
    """Search SympGAN symptoms by name

    Args:
        query: Search query string
        session: Database session
        limit: Maximum results to return

    Returns:
        List of matching symptoms
    """
    symptoms = await SympganSymptomService.search_by_name(session, query, limit)

    return SympganSymptomListResponse(
        total=len(symptoms),
        items=[
            SympganSymptomResponse(
                id=s.id,
                cui=s.cui,
                name=s.name,
                alias=s.alias,
                definition=s.definition,
                external_ids=s.external_ids,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in symptoms
        ],
    )


@router.patch("/sympgan-symptoms/{symptom_id}", response_model=SympganSymptomResponse)
async def update_sympgan_symptom(symptom_id: int, session: SessionDep, data: SympganSymptomUpdate):
    """Update a SympGAN symptom

    Args:
        symptom_id: Symptom ID
        session: Database session
        data: Update data

    Returns:
        Updated symptom

    Raises:
        HTTPException: If symptom not found
    """
    symptom = await SympganSymptomService.update(session, symptom_id, data)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")

    return SympganSymptomResponse(
        id=symptom.id,
        cui=symptom.cui,
        name=symptom.name,
        alias=symptom.alias,
        definition=symptom.definition,
        external_ids=symptom.external_ids,
        created_at=symptom.created_at,
        updated_at=symptom.updated_at,
    )


@router.delete("/sympgan-symptoms/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sympgan_symptom(symptom_id: int, session: SessionDep):
    """Delete a SympGAN symptom (and all associated diseases)

    Args:
        symptom_id: Symptom ID
        session: Database session

    Raises:
        HTTPException: If symptom not found
    """
    deleted = await SympganSymptomService.delete(session, symptom_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")


# ============================================================================
# SympGAN Disease-Symptom Association Endpoints
# ============================================================================


@router.post(
    "/sympgan-disease-symptom-associations",
    response_model=SympganDiseaseSymptomAssociationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sympgan_association(session: SessionDep, data: SympganDiseaseSymptomAssociationCreate):
    """Associate a disease with a symptom

    Args:
        session: Database session
        data: Association data

    Returns:
        Created association
    """
    association = await SympganDiseaseSymptomAssociationService.create_association(session, data)
    return association


@router.get("/sympgan-diseases/{disease_id}/symptoms", response_model=SympganSymptomListResponse)
async def get_sympgan_disease_symptoms(disease_id: int, session: SessionDep):
    """Get all symptoms associated with a disease

    Args:
        disease_id: Disease ID
        session: Database session

    Returns:
        List of symptoms
    """
    # Verify disease exists
    disease = await SympganDiseaseService.get(session, disease_id)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")

    symptoms = await SympganDiseaseSymptomAssociationService.get_symptoms_by_disease(
        session, disease_id
    )

    return SympganSymptomListResponse(
        total=len(symptoms),
        items=[
            SympganSymptomResponse(
                id=s.id,
                cui=s.cui,
                name=s.name,
                alias=s.alias,
                definition=s.definition,
                external_ids=s.external_ids,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in symptoms
        ],
    )


@router.get("/sympgan-symptoms/{symptom_id}/diseases", response_model=SympganDiseaseListResponse)
async def get_sympgan_symptom_diseases(symptom_id: int, session: SessionDep):
    """Get all diseases associated with a symptom

    Args:
        symptom_id: Symptom ID
        session: Database session

    Returns:
        List of diseases
    """
    # Verify symptom exists
    symptom = await SympganSymptomService.get(session, symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")

    diseases = await SympganDiseaseSymptomAssociationService.get_diseases_by_symptom(
        session, symptom_id
    )

    return SympganDiseaseListResponse(
        total=len(diseases),
        items=[
            SympganDiseaseResponse(
                id=d.id,
                cui=d.cui,
                name=d.name,
                alias=d.alias,
                definition=d.definition,
                external_ids=d.external_ids,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in diseases
        ],
    )


# ============================================================================
# Health Check Endpoint
# ============================================================================


@router.get("/health")
async def sqlite_health_check():
    """Check SQLite database health

    Returns:
        Health status response
    """
    is_healthy = await SQLiteClientWrapper.health_check()

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "SQLite",
    }
