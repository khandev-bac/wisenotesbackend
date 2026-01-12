import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class SourceTypeEnum(enum.Enum):
    AUDIO = "audio"
    YOUTUBE = "youtube"
    DOCUMENTS = "documents"


class Sources(Base):
    __tablename__ = "sources"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_type: Mapped[SourceTypeEnum] = mapped_column(
        Enum(SourceTypeEnum, name="source_type_enum"), nullable=False
    )
    source_url: Mapped[str] = mapped_column(String, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    user = relationship("Users", back_populates="sources")
    notes = relationship("Notes", back_populates="source", cascade="all, delete")
    jobs = relationship("Jobs", back_populates="source", cascade="all, delete")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
