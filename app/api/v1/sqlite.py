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
    ExclusionMethodCreate,
    ExclusionMethodListResponse,
    ExclusionMethodResponse,
    ExclusionMethodUpdate,
    TreatmentPlanCreate,
    TreatmentPlanListResponse,
    TreatmentPlanResponse,
    TreatmentPlanUpdate,
)
from app.services.sqlite_crud import (
    ConditionExclusionMethodService,
    ConditionService,
    ConditionTreatmentPlanService,
    ExclusionMethodService,
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
