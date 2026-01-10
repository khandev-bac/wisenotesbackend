import enum
import uuid
from datetime import datetime ,timezone
from sqlalchemy import Boolean,DateTime,Enum, ForeignKey,String,Integer
from sqlalchemy.orm import Mapped,mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..db import Base


class Status(enum.Enum):
    PENDING = "pending"
    DONE = "done"

class Notes(Base):
    __tablename__ = "notes"
    id:Mapped[uuid.UUID]= mapped_column(
    UUID(as_uuid=True),primary_key=True,
    default=uuid.uuid4
    )
    source_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id"),
        nullable=False
    )
    user_id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    title:Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    content:Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    summary:Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    status:Mapped[Status] = mapped_column(
        Enum(Status,name="status"),
        nullable=False
    )
    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        nullable=False
    )
    updated_at:Mapped[datetime] =  mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc),
        nullable=False
    )
    user = relationship("Users",back_populates="notes")
    source = relationship("Sources",back_populates="notes")
