"""SQLite Database Models and Client Wrapper

This module defines SQLAlchemy ORM models for Medi-Bridge database
and provides a client wrapper for database operations.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

from app.core.config import settings
from app.core.exceptions import SQLiteConnectionError


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key support for SQLite"""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    """Base class for all ORM models"""


# ============================================================================
# Database Models
# ============================================================================


class Disease(Base):
    """Disease model (SympGAN dataset)

    Stores disease information from SympGAN dataset.
    """

    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cui: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    alias: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    # Relationships
    symptom_associations: Mapped[list["DiseaseSymptomAssociation"]] = relationship(
        "DiseaseSymptomAssociation",
        back_populates="disease",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Disease(id={self.id}, cui='{self.cui}', name='{self.name}')>"


class Symptom(Base):
    """Symptom model (SympGAN dataset)

    Stores symptom information from SympGAN dataset.
    Extended with full_description and summary for rich content.
    """

    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cui: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    alias: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    external_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    # Relationships
    disease_associations: Mapped[list["DiseaseSymptomAssociation"]] = relationship(
        "DiseaseSymptomAssociation",
        back_populates="symptom",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Symptom(id={self.id}, cui='{self.cui}', name='{self.name}')>"


class DiseaseSymptomAssociation(Base):
    """Disease-symptom association model (SympGAN dataset)

    Many-to-many relationship between diseases and symptoms from SympGAN dataset.
    """

    __tablename__ = "disease_symptom_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disease_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("diseases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symptom_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("symptoms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    # Relationships
    disease: Mapped["Disease"] = relationship(
        "Disease", back_populates="symptom_associations"
    )
    symptom: Mapped["Symptom"] = relationship(
        "Symptom", back_populates="disease_associations"
    )

    def __repr__(self) -> str:
        return (
            f"<DiseaseSymptomAssociation(id={self.id}, "
            f"disease_id={self.disease_id}, symptom_id={self.symptom_id})>"
        )


class Conversation(Base):
    """Conversation model

    Records conversations between doctors and patients.
    Stores current progress of vector search results.
    """

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    patient_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    progress: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title='{self.title}', department='{self.department}')>"


class Message(Base):
    """Message model

    Records individual messages within a conversation.
    """

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sent_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )
    role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role='{self.role}')>"


# ============================================================================
# Client Wrapper
# ============================================================================


class SQLiteClientWrapper:
    """SQLite database client wrapper with lazy initialization

    This class provides a singleton-like interface to the async SQLite database.
    Tables are created automatically on first access.
    """

    _engine: Optional[AsyncSession] = None
    _session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    _initialized: bool = False

    @classmethod
    async def _ensure_tables_exist(cls) -> None:
        """Create all tables if they don't exist"""
        if cls._initialized:
            return

        # Build database URL for async SQLite
        db_url = f"sqlite+aiosqlite:///{settings.SQLITE_DATABASE_PATH}"

        # Create async engine
        cls._engine = create_async_engine(
            db_url,
            echo=settings.SQLITE_ECHO,
        )

        # Create session factory
        cls._session_factory = async_sessionmaker(
            bind=cls._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Create all tables
        async with cls._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        cls._initialized = True

    @classmethod
    async def get_session(cls) -> AsyncSession:
        """Get a new database session

        Returns:
            AsyncSession: A new SQLAlchemy async session

        Raises:
            SQLiteConnectionError: If database connection fails
        """
        if not cls._initialized:
            try:
                await cls._ensure_tables_exist()
            except Exception as e:
                raise SQLiteConnectionError(f"Failed to initialize database: {e}") from e

        if cls._session_factory is None:
            raise SQLiteConnectionError("Session factory not initialized")

        return cls._session_factory()

    @classmethod
    async def health_check(cls) -> bool:
        """Check if database connection is healthy

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            if not cls._initialized:
                await cls._ensure_tables_exist()

            session = await cls.get_session()
            await session.execute("SELECT 1")
            await session.close()
            return True
        except Exception:
            return False

    @classmethod
    async def close(cls) -> None:
        """Close database connection"""
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._initialized = False
            cls._engine = None
            cls._session_factory = None


# Global instance
sqlite_client = SQLiteClientWrapper
