import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class AuthProvider(enum.Enum):
    GOOGLE = "google"
    EMAIL = "email"


class Plan(enum.Enum):
    FREE = "free"
    PRO = "pro"



class Users(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    password: Mapped[str | None] = mapped_column(String, nullable=True)

    google_id: Mapped[str | None] = mapped_column(String, nullable=True)

    auth_provider: Mapped[AuthProvider] = mapped_column(
        Enum(AuthProvider, name="auth_provider"), nullable=False
    )

    profile_img: Mapped[str | None] = mapped_column(String, nullable=True)

    plan: Mapped[Plan] = mapped_column(
        Enum(Plan, name="plan"), default=Plan.FREE, nullable=False
    )

    user_device: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sources = relationship("Sources",back_populates="user",cascade="all, delete")
    notes = relationship("Notes",back_populates="user",cascade="all, delete")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
