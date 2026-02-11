"""CRUD Service Layer for SQLite Database

This module implements CRUD operations for all SQLite database entities.
"""
import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import SQLiteServiceError
from app.models.sqlite_db import (
    Conversation,
    Disease,
    DiseaseSymptomAssociation,
    Message,
    Symptom,
)
from app.schemas.sqlite import (
    DiseaseSymptomAssociationCreate,
    DiseaseUpdate,
    MessageUpdate,
    SymptomCreate,
    SymptomUpdate,
    ConversationUpdate,
)


# ============================================================================
# Disease Service
# ============================================================================


class DiseaseService:
    """CRUD operations for diseases (SympGAN dataset)"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> Disease:
        """Create a new disease

        Args:
            session: Database session
            data: Disease data dictionary

        Returns:
            Created disease object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            disease = Disease(**data)
            session.add(disease)
            await session.commit()
            await session.refresh(disease)
            return disease
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create disease: {e}") from e

    @staticmethod
    async def get_by_cui(session: AsyncSession, cui: str) -> Optional[Disease]:
        """Get a disease by CUI

        Args:
            session: Database session
            cui: Disease CUI

        Returns:
            Disease object or None if not found
        """
        try:
            stmt = select(Disease).where(Disease.cui == cui)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get disease: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, disease_id: int) -> Optional[Disease]:
        """Get a disease by ID

        Args:
            session: Database session
            disease_id: Disease ID

        Returns:
            Disease object or None if not found
        """
        try:
            stmt = select(Disease).where(Disease.id == disease_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get disease: {e}") from e

    @staticmethod
    async def get_with_symptoms(
        session: AsyncSession, disease_id: int
    ) -> Optional[Disease]:
        """Get a disease by ID with symptom associations loaded

        Args:
            session: Database session
            disease_id: Disease ID

        Returns:
            Disease object with symptoms or None if not found
        """
        try:
            stmt = (
                select(Disease)
                .where(Disease.id == disease_id)
                .options(
                    selectinload(Disease.symptom_associations).selectinload(
                        DiseaseSymptomAssociation.symptom
                    )
                )
            )
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get disease with symptoms: {e}") from e

    @staticmethod
    async def list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[Disease]]:
        """List all diseases with pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of diseases)
        """
        try:
            # Get total count
            count_stmt = select(func.count()).select_from(Disease)
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results
            stmt = select(Disease).offset(skip).limit(limit).order_by(Disease.id)
            result = await session.execute(stmt)
            diseases = result.scalars().all()

            return total, list(diseases)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list diseases: {e}") from e

    @staticmethod
    async def search_by_name(
        session: AsyncSession, query: str, limit: int = 10
    ) -> list[Disease]:
        """Search diseases by name (LIKE query)

        Args:
            session: Database session
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching diseases
        """
        try:
            stmt = (
                select(Disease)
                .where(Disease.name.ilike(f"%{query}%"))
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLiteServiceError(f"Failed to search diseases: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, disease_id: int, data: DiseaseUpdate
    ) -> Optional[Disease]:
        """Update a disease

        Args:
            session: Database session
            disease_id: Disease ID
            data: Update data

        Returns:
            Updated disease object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            disease = await DiseaseService.get(session, disease_id)
            if not disease:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(disease, field, value)

            await session.commit()
            await session.refresh(disease)
            return disease
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update disease: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, disease_id: int) -> bool:
        """Delete a disease

        Args:
            session: Database session
            disease_id: Disease ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            disease = await DiseaseService.get(session, disease_id)
            if not disease:
                return False

            await session.delete(disease)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete disease: {e}") from e


# ============================================================================
# Symptom Service
# ============================================================================


class SymptomService:
    """CRUD operations for symptoms (SympGAN dataset)"""

    @staticmethod
    async def create(session: AsyncSession, data: dict) -> Symptom:
        """Create a new symptom

        Args:
            session: Database session
            data: Symptom data dictionary

        Returns:
            Created symptom object

        Raises:
            SQLiteServiceError: If creation fails
        """
        try:
            symptom = Symptom(**data)
            session.add(symptom)
            await session.commit()
            await session.refresh(symptom)
            return symptom
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to create symptom: {e}") from e

    @staticmethod
    async def get_by_cui(session: AsyncSession, cui: str) -> Optional[Symptom]:
        """Get a symptom by CUI

        Args:
            session: Database session
            cui: Symptom CUI

        Returns:
            Symptom object or None if not found
        """
        try:
            stmt = select(Symptom).where(Symptom.cui == cui)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get symptom: {e}") from e

    @staticmethod
    async def get(session: AsyncSession, symptom_id: int) -> Optional[Symptom]:
        """Get a symptom by ID

        Args:
            session: Database session
            symptom_id: Symptom ID

        Returns:
            Symptom object or None if not found
        """
        try:
            stmt = select(Symptom).where(Symptom.id == symptom_id)
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get symptom: {e}") from e

    @staticmethod
    async def get_with_diseases(
        session: AsyncSession, symptom_id: int
    ) -> Optional[Symptom]:
        """Get a symptom by ID with disease associations loaded

        Args:
            session: Database session
            symptom_id: Symptom ID

        Returns:
            Symptom object with diseases or None if not found
        """
        try:
            stmt = (
                select(Symptom)
                .where(Symptom.id == symptom_id)
                .options(
                    selectinload(Symptom.disease_associations).selectinload(
                        DiseaseSymptomAssociation.disease
                    )
                )
            )
            result = await session.execute(stmt)
            return result.scalars().first()
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get symptom with diseases: {e}") from e

    @staticmethod
    async def list(
        session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[int, list[Symptom]]:
        """List all symptoms with pagination

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (total count, list of symptoms)
        """
        try:
            # Get total count
            count_stmt = select(func.count()).select_from(Symptom)
            count_result = await session.execute(count_stmt)
            total = count_result.scalar()

            # Get paginated results
            stmt = select(Symptom).offset(skip).limit(limit).order_by(Symptom.id)
            result = await session.execute(stmt)
            symptoms = result.scalars().all()

            return total, list(symptoms)
        except Exception as e:
            raise SQLiteServiceError(f"Failed to list symptoms: {e}") from e

    @staticmethod
    async def search_by_name(
        session: AsyncSession, query: str, limit: int = 10
    ) -> list[Symptom]:
        """Search symptoms by name (LIKE query)

        Args:
            session: Database session
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of matching symptoms
        """
        try:
            stmt = (
                select(Symptom)
                .where(Symptom.name.ilike(f"%{query}%"))
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLiteServiceError(f"Failed to search symptoms: {e}") from e

    @staticmethod
    async def update(
        session: AsyncSession, symptom_id: int, data: SymptomUpdate
    ) -> Optional[Symptom]:
        """Update a symptom

        Args:
            session: Database session
            symptom_id: Symptom ID
            data: Update data

        Returns:
            Updated symptom object or None if not found

        Raises:
            SQLiteServiceError: If update fails
        """
        try:
            symptom = await SymptomService.get(session, symptom_id)
            if not symptom:
                return None

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(symptom, field, value)

            await session.commit()
            await session.refresh(symptom)
            return symptom
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to update symptom: {e}") from e

    @staticmethod
    async def delete(session: AsyncSession, symptom_id: int) -> bool:
        """Delete a symptom

        Args:
            session: Database session
            symptom_id: Symptom ID

        Returns:
            True if deleted, False if not found

        Raises:
            SQLiteServiceError: If deletion fails
        """
        try:
            symptom = await SymptomService.get(session, symptom_id)
            if not symptom:
                return False

            await session.delete(symptom)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise SQLiteServiceError(f"Failed to delete symptom: {e}") from e


# ============================================================================
# Disease-Symptom Association Service
# ============================================================================


class DiseaseSymptomAssociationService:
    """Service for managing disease-symptom associations from SympGAN dataset"""

    @staticmethod
    async def create_association(
        session: AsyncSession, data: DiseaseSymptomAssociationCreate
    ) -> DiseaseSymptomAssociation:
        """Associate a disease with a symptom

        Args:
            session: Database session
            data: Association data

        Returns:
            Created association object

        Raises:
            SQLiteServiceError: If association creation fails
        """
        try:
            # Verify disease exists
            disease = await DiseaseService.get(session, data.disease_id)
            if not disease:
                raise SQLiteServiceError(f"Disease with ID {data.disease_id} not found")

            # Verify symptom exists
            symptom = await SymptomService.get(session, data.symptom_id)
            if not symptom:
                raise SQLiteServiceError(f"Symptom with ID {data.symptom_id} not found")

            # Check if association already exists
            existing = (
                select(DiseaseSymptomAssociation)
                .where(
                    DiseaseSymptomAssociation.disease_id == data.disease_id,
                    DiseaseSymptomAssociation.symptom_id == data.symptom_id,
                )
            )
            result = await session.execute(existing)
            if result.scalars().first():
                # Association already exists, return it
                return result.scalars().first()

            association = DiseaseSymptomAssociation(
                disease_id=data.disease_id,
                symptom_id=data.symptom_id,
                source=data.source,
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
    async def get_symptoms_by_disease(
        session: AsyncSession, disease_id: int
    ) -> list[Symptom]:
        """Get all symptoms associated with a disease

        Args:
            session: Database session
            disease_id: Disease ID

        Returns:
            List of symptoms

        Raises:
            SQLiteServiceError: If query fails
        """
        try:
            stmt = (
                select(Symptom)
                .join(DiseaseSymptomAssociation)
                .where(DiseaseSymptomAssociation.disease_id == disease_id)
                .order_by(Symptom.id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get symptoms: {e}") from e

    @staticmethod
    async def get_diseases_by_symptom(
        session: AsyncSession, symptom_id: int
    ) -> list[Disease]:
        """Get all diseases associated with a symptom

        Args:
            session: Database session
            symptom_id: Symptom ID

        Returns:
            List of diseases

        Raises:
            SQLiteServiceError: If query fails
        """
        try:
            stmt = (
                select(Disease)
                .join(DiseaseSymptomAssociation)
                .where(DiseaseSymptomAssociation.symptom_id == symptom_id)
                .order_by(Disease.id)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise SQLiteServiceError(f"Failed to get diseases: {e}") from e


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
        """Delete a conversation (and all associated messages)

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
