"""SQLite Database API Endpoints

This module provides REST API endpoints for managing SQLite database entities.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.sqlite_db import SQLiteClientWrapper
from app.schemas.sqlite import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessagesResponse,
    DiseaseCreate,
    DiseaseListResponse,
    DiseaseResponse,
    DiseaseSymptomAssociationCreate,
    DiseaseSymptomAssociationResponse,
    DiseaseUpdate,
    DiseaseWithSymptomsResponse,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    MessageUpdate,
    SymptomCreate,
    SymptomListResponse,
    SymptomResponse,
    SymptomUpdate,
    SymptomWithDiseasesResponse,
)
from app.services.sqlite_crud import (
    ConversationService,
    DiseaseService,
    DiseaseSymptomAssociationService,
    MessageService,
    SymptomService,
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
# Disease Endpoints
# ============================================================================


@router.post("/diseases", response_model=DiseaseResponse, status_code=status.HTTP_201_CREATED)
async def create_disease(session: SessionDep, data: DiseaseCreate):
    """Create a new disease

    Args:
        session: Database session
        data: Disease creation data

    Returns:
        Created disease
    """
    disease = await DiseaseService.create(session, data.model_dump())
    return disease


@router.get("/diseases/{disease_id}", response_model=DiseaseWithSymptomsResponse)
async def get_disease(disease_id: int, session: SessionDep):
    """Get a disease by ID with symptoms

    Args:
        disease_id: Disease ID
        session: Database session

    Returns:
        Disease with symptoms

    Raises:
        HTTPException: If disease not found
    """
    disease = await DiseaseService.get_with_symptoms(session, disease_id)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")

    # Build symptoms list
    symptoms = [
        SymptomResponse(
            id=assoc.symptom.id,
            cui=assoc.symptom.cui,
            name=assoc.symptom.name,
            alias=assoc.symptom.alias,
            definition=assoc.symptom.definition,
            external_ids=assoc.symptom.external_ids,
            full_description=assoc.symptom.full_description,
            summary=assoc.symptom.summary,
            created_at=assoc.symptom.created_at,
        )
        for assoc in disease.symptom_associations
    ]

    return DiseaseWithSymptomsResponse(
        id=disease.id,
        cui=disease.cui,
        name=disease.name,
        alias=disease.alias,
        definition=disease.definition,
        external_ids=disease.external_ids,
        created_at=disease.created_at,
        symptoms=symptoms,
    )


@router.get("/diseases", response_model=DiseaseListResponse)
async def list_diseases(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all diseases with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of diseases
    """
    total, diseases = await DiseaseService.list(session, skip=skip, limit=limit)

    return DiseaseListResponse(
        total=total,
        items=[
            DiseaseResponse(
                id=d.id,
                cui=d.cui,
                name=d.name,
                alias=d.alias,
                definition=d.definition,
                external_ids=d.external_ids,
                created_at=d.created_at,
            )
            for d in diseases
        ],
    )


@router.get("/diseases/search/{query}", response_model=DiseaseListResponse)
async def search_diseases(
    query: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results to return")] = 10,
):
    """Search diseases by name

    Args:
        query: Search query string
        session: Database session
        limit: Maximum results to return

    Returns:
        List of matching diseases
    """
    diseases = await DiseaseService.search_by_name(session, query, limit)

    return DiseaseListResponse(
        total=len(diseases),
        items=[
            DiseaseResponse(
                id=d.id,
                cui=d.cui,
                name=d.name,
                alias=d.alias,
                definition=d.definition,
                external_ids=d.external_ids,
                created_at=d.created_at,
            )
            for d in diseases
        ],
    )


@router.patch("/diseases/{disease_id}", response_model=DiseaseResponse)
async def update_disease(disease_id: int, session: SessionDep, data: DiseaseUpdate):
    """Update a disease

    Args:
        disease_id: Disease ID
        session: Database session
        data: Update data

    Returns:
        Updated disease

    Raises:
        HTTPException: If disease not found
    """
    disease = await DiseaseService.update(session, disease_id, data)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")

    return DiseaseResponse(
        id=disease.id,
        cui=disease.cui,
        name=disease.name,
        alias=disease.alias,
        definition=disease.definition,
        external_ids=disease.external_ids,
        created_at=disease.created_at,
    )


@router.delete("/diseases/{disease_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disease(disease_id: int, session: SessionDep):
    """Delete a disease

    Args:
        disease_id: Disease ID
        session: Database session

    Raises:
        HTTPException: If disease not found
    """
    deleted = await DiseaseService.delete(session, disease_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")


# ============================================================================
# Symptom Endpoints
# ============================================================================


@router.post("/symptoms", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom(session: SessionDep, data: SymptomCreate):
    """Create a new symptom

    Args:
        session: Database session
        data: Symptom creation data

    Returns:
        Created symptom
    """
    symptom = await SymptomService.create(session, data.model_dump())
    return symptom


@router.get("/symptoms/{symptom_id}", response_model=SymptomWithDiseasesResponse)
async def get_symptom(symptom_id: int, session: SessionDep):
    """Get a symptom by ID with diseases

    Args:
        symptom_id: Symptom ID
        session: Database session

    Returns:
        Symptom with diseases

    Raises:
        HTTPException: If symptom not found
    """
    symptom = await SymptomService.get_with_diseases(session, symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")

    # Build diseases list
    diseases = [
        DiseaseResponse(
            id=assoc.disease.id,
            cui=assoc.disease.cui,
            name=assoc.disease.name,
            alias=assoc.disease.alias,
            definition=assoc.disease.definition,
            external_ids=assoc.disease.external_ids,
            created_at=assoc.disease.created_at,
        )
        for assoc in symptom.disease_associations
    ]

    return SymptomWithDiseasesResponse(
        id=symptom.id,
        cui=symptom.cui,
        name=symptom.name,
        alias=symptom.alias,
        definition=symptom.definition,
        external_ids=symptom.external_ids,
        full_description=symptom.full_description,
        summary=symptom.summary,
        created_at=symptom.created_at,
        diseases=diseases,
    )


@router.get("/symptoms", response_model=SymptomListResponse)
async def list_symptoms(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum records to return")] = 100,
):
    """List all symptoms with pagination

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of symptoms
    """
    total, symptoms = await SymptomService.list(session, skip=skip, limit=limit)

    return SymptomListResponse(
        total=total,
        items=[
            SymptomResponse(
                id=s.id,
                cui=s.cui,
                name=s.name,
                alias=s.alias,
                definition=s.definition,
                external_ids=s.external_ids,
                full_description=s.full_description,
                summary=s.summary,
                created_at=s.created_at,
            )
            for s in symptoms
        ],
    )


@router.get("/symptoms/search/{query}", response_model=SymptomListResponse)
async def search_symptoms(
    query: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results to return")] = 10,
):
    """Search symptoms by name

    Args:
        query: Search query string
        session: Database session
        limit: Maximum results to return

    Returns:
        List of matching symptoms
    """
    symptoms = await SymptomService.search_by_name(session, query, limit)

    return SymptomListResponse(
        total=len(symptoms),
        items=[
            SymptomResponse(
                id=s.id,
                cui=s.cui,
                name=s.name,
                alias=s.alias,
                definition=s.definition,
                external_ids=s.external_ids,
                full_description=s.full_description,
                summary=s.summary,
                created_at=s.created_at,
            )
            for s in symptoms
        ],
    )


@router.patch("/symptoms/{symptom_id}", response_model=SymptomResponse)
async def update_symptom(symptom_id: int, session: SessionDep, data: SymptomUpdate):
    """Update a symptom

    Args:
        symptom_id: Symptom ID
        session: Database session
        data: Update data

    Returns:
        Updated symptom

    Raises:
        HTTPException: If symptom not found
    """
    symptom = await SymptomService.update(session, symptom_id, data)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")

    return SymptomResponse(
        id=symptom.id,
        cui=symptom.cui,
        name=symptom.name,
        alias=symptom.alias,
        definition=symptom.definition,
        external_ids=symptom.external_ids,
        full_description=symptom.full_description,
        summary=symptom.summary,
        created_at=symptom.created_at,
    )


@router.delete("/symptoms/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symptom(symptom_id: int, session: SessionDep):
    """Delete a symptom

    Args:
        symptom_id: Symptom ID
        session: Database session

    Raises:
        HTTPException: If symptom not found
    """
    deleted = await SymptomService.delete(session, symptom_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")


# ============================================================================
# Disease-Symptom Association Endpoints
# ============================================================================


@router.post(
    "/disease-symptom-associations",
    response_model=DiseaseSymptomAssociationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_disease_symptom_association(
    session: SessionDep, data: DiseaseSymptomAssociationCreate
):
    """Associate a disease with a symptom

    Args:
        session: Database session
        data: Association data

    Returns:
        Created association
    """
    association = await DiseaseSymptomAssociationService.create_association(session, data)
    return association


@router.get("/diseases/{disease_id}/symptoms", response_model=SymptomListResponse)
async def get_disease_symptoms(disease_id: int, session: SessionDep):
    """Get all symptoms associated with a disease

    Args:
        disease_id: Disease ID
        session: Database session

    Returns:
        List of symptoms

    Raises:
        HTTPException: If disease not found
    """
    # Verify disease exists
    disease = await DiseaseService.get(session, disease_id)
    if not disease:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found")

    symptoms = await DiseaseSymptomAssociationService.get_symptoms_by_disease(
        session, disease_id
    )

    return SymptomListResponse(
        total=len(symptoms),
        items=[
            SymptomResponse(
                id=s.id,
                cui=s.cui,
                name=s.name,
                alias=s.alias,
                definition=s.definition,
                external_ids=s.external_ids,
                full_description=s.full_description,
                summary=s.summary,
                created_at=s.created_at,
            )
            for s in symptoms
        ],
    )


@router.get("/symptoms/{symptom_id}/diseases", response_model=DiseaseListResponse)
async def get_symptom_diseases(symptom_id: int, session: SessionDep):
    """Get all diseases associated with a symptom

    Args:
        symptom_id: Symptom ID
        session: Database session

    Returns:
        List of diseases

    Raises:
        HTTPException: If symptom not found
    """
    # Verify symptom exists
    symptom = await SymptomService.get(session, symptom_id)
    if not symptom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symptom not found")

    diseases = await DiseaseSymptomAssociationService.get_diseases_by_symptom(
        session, symptom_id
    )

    return DiseaseListResponse(
        total=len(diseases),
        items=[
            DiseaseResponse(
                id=d.id,
                cui=d.cui,
                name=d.name,
                alias=d.alias,
                definition=d.definition,
                external_ids=d.external_ids,
                created_at=d.created_at,
            )
            for d in diseases
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
