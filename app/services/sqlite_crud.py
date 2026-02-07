"""CRUD Service Layer for SQLite Database

This module implements CRUD operations for all SQLite database entities.
"""
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SQLiteServiceError
from app.models.sqlite_db import (
    Condition,
    ConditionExclusionMethod,
    ConditionTreatmentPlan,
    Conversation,
    ExclusionMethod,
    Message,
    TreatmentPlan,
)
from app.schemas.sqlite import (
    ConditionExclusionMethodCreate,
    ConditionTreatmentPlanCreate,
    ConditionTreatmentPlanUpdate,
    ConditionUpdate,
    ConversationUpdate,
    ExclusionMethodUpdate,
    MessageUpdate,
    TreatmentPlanUpdate,
)


# ============================================================================
# Condition Service
# ============================================================================


class ConditionService:
    """CRUD operations for conditions"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> Condition:
        """Create a new condition

        Args:
            session: Database session
            data: Condition data dictionary

        Returns:
            Created condition object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            condition = Condition(**data)
            session.add(condition)
            await session.commit()
            await session.refresh(condition)
            return condition
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create condition: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, condition_id: int) -> Optional[Condition]:
        """Get a condition by ID

        Args:
            session: Database session
            condition_id: Condition ID

        Returns:
            Condition object or None if not found
        """
        try:
            stmt = select(Condition).where(Condition.id == condition_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get condition: {e}") from e

    @staticmethod
    async def get_with_relationships(
        session: AsyncSession, condition_id: int
    ) -> Optional[Condition]:
        """Get a condition by ID with relationships loaded

        Args:
            session: Database session
            condition_id: Condition ID

        Returns:
            Condition object with relationships or None if not found
        """
        try:
            stmt = (
                select(Condition)
                .where(Condition.id == condition_id)
                .options(
                    selectinload(Condition.exclusion_methods).selectinload(
                        ConditionExclusionMethod.exclusion_method
                    ),
                    selectinload(Condition.treatment_plans).selectinload(
                        ConditionTreatmentPlan.treatment_plan
                    ),
                )
            )
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get condition with relationships: {e}") from e

    @staticmethod
    async def list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[Condition]]:
        """List all conditions with pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of conditions)
        """
        try:
            # Get total count
            count_stmt = select(func.count()).select_from(Condition)
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results
            stmt = select(Condition).offset(skip).limit(limit).order_by(Condition.id)
            result = await session.execute(stmt)
            conditions = result.scalars().all()

            return total, list(conditions)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list conditions: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, condition_id: int, data: ConditionUpdate
    ) -> Optional[Condition]:
        """Update a condition

        Args:
            session: Database session
            condition_id: Condition ID
            data: Update data

        Returns:
            Updated condition object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            condition = await ConditionService.get(session, condition_id)
            if not condition:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(condition, field, value)

            await session.commit()
            await session.refresh(condition)
            return condition
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update condition: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, condition_id: int) -> bool:
        """Delete a condition

        Args:
            session: Database session
            condition_id: Condition ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            condition = await ConditionService.get(session, condition_id)
            if not condition:
                return False

            await session.delete(condition)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete condition: {e}") from e


# ============================================================================
# Exclusion Method Service
# ============================================================================


class ExclusionMethodService:
    """CRUD operations for exclusion methods"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> ExclusionMethod:
        """Create a new exclusion method

        Args:
            session: Database session
            data: Exclusion method data dictionary

        Returns:
            Created exclusion method object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            exclusion_method = ExclusionMethod(**data)
            session.add(exclusion_method)
            await session.commit()
            await session.refresh(exclusion_method)
            return exclusion_method
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create exclusion method: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, method_id: int) -> Optional[ExclusionMethod]:
        """Get an exclusion method by ID

        Args:
            session: Database session
            method_id: Exclusion method ID

        Returns:
            Exclusion method object or None if not found
        """
        try:
            stmt = select(ExclusionMethod).where(ExclusionMethod.id == method_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get exclusion method: {e}") from e

    @staticmethod
    async def list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[ExclusionMethod]]:
        """List all exclusion methods with pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of exclusion methods)
        """
        try:
            # Get total count
            count_stmt = select(func.count()).select_from(ExclusionMethod)
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results
            stmt = select(ExclusionMethod).offset(skip).limit(limit).order_by(ExclusionMethod.id)
            result = await session.execute(stmt)
            methods = result.scalars().all()

            return total, list(methods)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list exclusion methods: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, method_id: int, data: ExclusionMethodUpdate
    ) -> Optional[ExclusionMethod]:
        """Update an exclusion method

        Args:
            session: Database session
            method_id: Exclusion method ID
            data: Update data

        Returns:
            Updated exclusion method object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            method = await ExclusionMethodService.get(session, method_id)
            if not method:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(method, field, value)

            await session.commit()
            await session.refresh(method)
            return method
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update exclusion method: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, method_id: int) -> bool:
        """Delete an exclusion method

        Args:
            session: Database session
            method_id: Exclusion method ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            method = await ExclusionMethodService.get(session, method_id)
            if not method:
                return False

            await session.delete(method)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete exclusion method: {e}") from e


# ============================================================================
# Treatment Plan Service
# ============================================================================


class TreatmentPlanService:
    """CRUD operations for treatment plans"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> TreatmentPlan:
        """Create a new treatment plan

        Args:
            session: Database session
            data: Treatment plan data dictionary

        Returns:
            Created treatment plan object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            treatment_plan = TreatmentPlan(**data)
            session.add(treatment_plan)
            await session.commit()
            await session.refresh(treatment_plan)
            return treatment_plan
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create treatment plan: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, plan_id: int) -> Optional[TreatmentPlan]:
        """Get a treatment plan by ID

        Args:
            session: Database session
            plan_id: Treatment plan ID

        Returns:
            Treatment plan object or None if not found
        """
        try:
            stmt = select(TreatmentPlan).where(TreatmentPlan.id == plan_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get treatment plan: {e}") from e

    @staticmethod
    async def list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[TreatmentPlan]]:
        """List all treatment plans with pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of treatment plans)
        """
        try:
            # Get total count
            count_stmt = select(func.count()).select_from(TreatmentPlan)
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results
            stmt = select(TreatmentPlan).offset(skip).limit(limit).order_by(TreatmentPlan.id)
            result = await session.execute(stmt)
            plans = result.scalars().all()

            return total, list(plans)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list treatment plans: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, plan_id: int, data: TreatmentPlanUpdate
    ) -> Optional[TreatmentPlan]:
        """Update a treatment plan

        Args:
            session: Database session
            plan_id: Treatment plan ID
            data: Update data

        Returns:
            Updated treatment plan object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            plan = await TreatmentPlanService.get(session, plan_id)
            if not plan:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(plan, field, value)

            await session.commit()
            await session.refresh(plan)
            return plan
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update treatment plan: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, plan_id: int) -> bool:
        """Delete a treatment plan

        Args:
            session: Database session
            plan_id: Treatment plan ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            plan = await TreatmentPlanService.get(session, plan_id)
            if not plan:
                return False

            await session.delete(plan)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete treatment plan: {e}") from e


# ============================================================================
# Association Management Services
# ============================================================================


class ConditionExclusionMethodService:
    """Service for managing condition-exclusion method associations"""

    @staticmethod
    async def add_association(
        session: AsyncSession, data: ConditionExclusionMethodCreate
    ) -> ConditionExclusionMethod:
        """Associate a condition with an exclusion method

        Args:
            session: Database session
            data: Association data

        Returns:
            Created association object

        Raises:
            SQLiteServiceError: If association creation fails
        """
        try:
            # Verify condition exists
            condition = await ConditionService.get(session, data.condition_id)
            if not condition:
                raise SQLiteServiceError(f"Condition with ID {data.condition_id} not found")

            # Verify exclusion method exists
            method = await ExclusionMethodService.get(session, data.exclusion_method_id)
            if not method:
                raise SQLiteServiceError(
                    f"Exclusion method with ID {data.exclusion_method_id} not found"
                )

            # Check if association already exists
            existing = (
                select(ConditionExclusionMethod).where(
                    ConditionExclusionMethod.condition_id == data.condition_id,
                    ConditionExclusionMethod.exclusion_method_id == data.exclusion_method_id,
                )
            )
            result = await session.execute(existing)
            if result.scalars().first():
                raise SQLiteServiceError("Association already exists")

            association = ConditionExclusionMethod(
                condition_id=data.condition_id,
                exclusion_method_id=data.exclusion_method_id,
            )
            session.add(association)
            await session.commit()
            await session.refresh(association)
            return association
        except SQLiteServiceError:
            raise
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create association: {e}") from e

    @staticmethod
    async def remove_association(session: AsyncSession, association_id: int) -> bool:
        """Remove a condition-exclusion method association

        Args:
            session: Database session
            association_id: Association ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            stmt = select(ConditionExclusionMethod).where(
                ConditionExclusionMethod.id == association_id
            )
            result = await session.execute(stmt)
            association = result.scalars().first()

            if not association:
                return False

            await session.delete(association)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to remove association: {e}") from e

    @staticmethod
    async def get_condition_exclusion_methods(
        session: AsyncSession, condition_id: int
    ) -> list[ExclusionMethod]:
        """Get all exclusion methods for a condition

        Args:
            session: Database session
            condition_id: Condition ID

        Returns:
            List of exclusion methods

        Raises:
            SQLiteServiceError: If query fails
        """
        try:
            stmt = (
                select(ExclusionMethod)
                .join(ConditionExclusionMethod)
                .where(ConditionExclusionMethod.condition_id == condition_id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get exclusion methods: {e}") from e


class ConditionTreatmentPlanService:
    """Service for managing condition-treatment plan associations"""

    @staticmethod
    async def add_association(
        session: AsyncSession, data: ConditionTreatmentPlanCreate
    ) -> ConditionTreatmentPlan:
        """Associate a condition with a treatment plan

        Args:
            session: Database session
            data: Association data

        Returns:
            Created association object

        Raises:
            SQLiteServiceError: If association creation fails
        """
        try:
            # Verify condition exists
            condition = await ConditionService.get(session, data.condition_id)
            if not condition:
                raise SQLiteServiceError(f"Condition with ID {data.condition_id} not found")

            # Verify treatment plan exists
            plan = await TreatmentPlanService.get(session, data.treatment_plan_id)
            if not plan:
                raise SQLiteServiceError(f"Treatment plan with ID {data.treatment_plan_id} not found")

            association = ConditionTreatmentPlan(
                condition_id=data.condition_id,
                treatment_plan_id=data.treatment_plan_id,
                is_primary=data.is_primary,
                priority=data.priority,
                notes=data.notes,
            )
            session.add(association)
            await session.commit()
            await session.refresh(association)
            return association
        except SQLiteServiceError:
            raise
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create association: {e}") from e

    @staticmethod
    async def update_association(
        session: AsyncSession, association_id: int, data: ConditionTreatmentPlanUpdate
    ) -> Optional[ConditionTreatmentPlan]:
        """Update a condition-treatment plan association

        Args:
            session: Database session
            association_id: Association ID
            data: Update data

        Returns:
            Updated association object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            stmt = select(ConditionTreatmentPlan).where(
                ConditionTreatmentPlan.id == association_id
            )
            result = await session.execute(stmt)
            association = result.scalars().first()

            if not association:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(association, field, value)

            await session.commit()
            await session.refresh(association)
            return association
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update association: {e}") from e

    @staticmethod
    async def remove_association(session: AsyncSession, association_id: int) -> bool:
        """Remove a condition-treatment plan association

        Args:
            session: Database session
            association_id: Association ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            stmt = select(ConditionTreatmentPlan).where(
                ConditionTreatmentPlan.id == association_id
            )
            result = await session.execute(stmt)
            association = result.scalars().first()

            if not association:
                return False

            await session.delete(association)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to remove association: {e}") from e

    @staticmethod
    async def get_condition_treatment_plans(
        session: AsyncSession, condition_id: int
    ) -> list[TreatmentPlan]:
        """Get all treatment plans for a condition

        Args:
            session: Database session
            condition_id: Condition ID

        Returns:
            List of treatment plans

        Raises:
            SQLiteServiceError: If query fails
        """
        try:
            stmt = (
                select(TreatmentPlan)
                .join(ConditionTreatmentPlan)
                .where(ConditionTreatmentPlan.condition_id == condition_id)
                .order_by(ConditionTreatmentPlan.priority.desc())
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get treatment plans: {e}") from e


# ============================================================================
# Conversation Service
# ============================================================================


class ConversationService:
    """CRUD operations for conversations"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> Conversation:
        """Create a new conversation

        Args:
            session: Database session
            data: Conversation data dictionary

        Returns:
            Created conversation object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            conversation = Conversation(**data)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create conversation: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID

        Args:
            session: Database session
            conversation_id: Conversation ID

        Returns:
            Conversation object or None if not found
        """
        try:
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get conversation: {e}") from e

    @staticmethod
    async def get_with_messages(
        session: AsyncSession, conversation_id: int
    ) -> Optional[Conversation]:
        """Get a conversation by ID with messages loaded

        Args:
            session: Database session
            conversation_id: Conversation ID

        Returns:
            Conversation object with messages or None if not found
        """
        try:
            stmt = (
                select(Conversation)
                .where(Conversation.id == conversation_id)
                .options(selectinload(Conversation.messages))
            )
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get conversation with messages: {e}") from e

    @staticmethod
    async def list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[Conversation]]:
        """List all conversations with pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of conversations)
        """
        try:
            # Get total count
            count_stmt = select(func.count()).select_from(Conversation)
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results (most recent first)
            stmt = (
                select(Conversation)
                .offset(skip)
                .limit(limit)
                .order_by(Conversation.started_at.desc())
            )
            result = await session.execute(stmt)
            conversations = result.scalars().all()

            return total, list(conversations)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list conversations: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, conversation_id: int, data: ConversationUpdate
    ) -> Optional[Conversation]:
        """Update a conversation

        Args:
            session: Database session
            conversation_id: Conversation ID
            data: Update data

        Returns:
            Updated conversation object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            conversation = await ConversationService.get(session, conversation_id)
            if not conversation:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(conversation, field, value)

            await session.commit()
            await session.refresh(conversation)
            return conversation
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update conversation: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, conversation_id: int) -> bool:
        """Delete a conversation (and all associated messages via CASCADE)

        Args:
            session: Database session
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            conversation = await ConversationService.get(session, conversation_id)
            if not conversation:
                return False

            await session.delete(conversation)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete conversation: {e}") from e


# ============================================================================
# Message Service
# ============================================================================


class MessageService:
    """CRUD operations for messages"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> Message:
        """Create a new message

        Args:
            session: Database session
            data: Message data dictionary

        Returns:
            Created message object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            # Verify conversation exists
            conversation = await ConversationService.get(session, data.get("conversation_id"))
            if not conversation:
                raise SQLiteServiceError(
                    f"Conversation with ID {data.get('conversation_id')} not found"
                )

            message = Message(**data)
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message
        except SQLiteServiceError:
            raise
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create message: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, message_id: int) -> Optional[Message]:
        """Get a message by ID

        Args:
            session: Database session
            message_id: Message ID

        Returns:
            Message object or None if not found
        """
        try:
            stmt = select(Message).where(Message.id == message_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get message: {e}") from e

    @staticmethod
    async def list_by_conversation(
        session: AsyncSession, conversation_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[Message]]:
        """List all messages in a conversation with pagination

        Args:
            session: Database session
            conversation_id: Conversation ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of messages)
        """
        try:
            # Get total count for this conversation
            count_stmt = (
                select(func.count())
                .select_from(Message)
                .where(Message.conversation_id == conversation_id)
            )
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results (oldest first for chat history)
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .offset(skip)
                .limit(limit)
                .order_by(Message.sent_at.asc())
            )
            result = await session.execute(stmt)
            messages = result.scalars().all()

            return total, list(messages)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list messages: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, message_id: int, data: MessageUpdate
    ) -> Optional[Message]:
        """Update a message

        Args:
            session: Database session
            message_id: Message ID
            data: Update data

        Returns:
            Updated message object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            message = await MessageService.get(session, message_id)
            if not message:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(message, field, value)

            await session.commit()
            await session.refresh(message)
            return message
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update message: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, message_id: int) -> bool:
        """Delete a message

        Args:
            session: Database session
            message_id: Message ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            message = await MessageService.get(session, message_id)
            if not message:
                return False

            await session.delete(message)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete message: {e}") from e
