"""SQLite Database Models and Client Wrapper

This module defines SQLAlchemy ORM models for the Medi-Bridge database
and provides a client wrapper for database operations.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
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


class Condition(Base):
    """Medical condition model

    Stores complete medical condition information with a summary
    for Qdrant payload.
    """

    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_description: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    # Relationships
    exclusion_methods: Mapped[list["ConditionExclusionMethod"]] = relationship(
        "ConditionExclusionMethod", back_populates="condition", cascade="all, delete-orphan"
    )
    treatment_plans: Mapped[list["ConditionTreatmentPlan"]] = relationship(
        "ConditionTreatmentPlan", back_populates="condition", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Condition(id={self.id}, name='{self.name}')>"


class ExclusionMethod(Base):
    """Exclusion method model

    Stores methods to exclude similar conditions during diagnosis.
    """

    __tablename__ = "exclusion_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    procedure_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    # Relationships
    conditions: Mapped[list["ConditionExclusionMethod"]] = relationship(
        "ConditionExclusionMethod", back_populates="exclusion_method", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ExclusionMethod(id={self.id}, name='{self.name}')>"


class ConditionExclusionMethod(Base):
    """Junction table for condition-exclusion method relationships

    Many-to-many relationship between conditions and exclusion methods.
    """

    __tablename__ = "condition_exclusion_methods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    condition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conditions.id", ondelete="CASCADE"),
        nullable=False,
    )
    exclusion_method_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("exclusion_methods.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    # Relationships
    condition: Mapped["Condition"] = relationship("Condition", back_populates="exclusion_methods")
    exclusion_method: Mapped["ExclusionMethod"] = relationship(
        "ExclusionMethod", back_populates="conditions"
    )

    def __repr__(self) -> str:
        return (
            f"<ConditionExclusionMethod(id={self.id}, "
            f"condition_id={self.condition_id}, exclusion_method_id={self.exclusion_method_id})>"
        )


class TreatmentPlan(Base):
    """Treatment plan model

    Stores treatment plans including medications, procedures,
    and influencing factors.
    """

    __tablename__ = "treatment_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    medications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    procedures: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    factors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contraindications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    # Relationships
    conditions: Mapped[list["ConditionTreatmentPlan"]] = relationship(
        "ConditionTreatmentPlan", back_populates="treatment_plan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TreatmentPlan(id={self.id}, name='{self.name}')>"


class ConditionTreatmentPlan(Base):
    """Junction table for condition-treatment plan relationships

    Many-to-one relationship (conditions -> treatment plans).
    Each condition has its own treatment plan entries for clinical precision.
    """

    __tablename__ = "condition_treatment_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    condition_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("conditions.id", ondelete="CASCADE"),
        nullable=False,
    )
    treatment_plan_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("treatment_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.utcnow()
    )

    # Relationships
    condition: Mapped["Condition"] = relationship("Condition", back_populates="treatment_plans")
    treatment_plan: Mapped["TreatmentPlan"] = relationship(
        "TreatmentPlan", back_populates="conditions"
    )

    def __repr__(self) -> str:
        return (
            f"<ConditionTreatmentPlan(id={self.id}, "
            f"condition_id={self.condition_id}, treatment_plan_id={self.treatment_plan_id})>"
        )


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
        """Close the database connection"""
        if cls._engine is not None:
            await cls._engine.dispose()
            cls._initialized = False
            cls._engine = None
            cls._session_factory = None
