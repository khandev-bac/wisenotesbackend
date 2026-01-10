import enum
import uuid
from datetime import datetime ,timezone
from sqlalchemy import Boolean,DateTime,Enum, ForeignKey,String,Integer
from sqlalchemy.orm import Mapped,mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..db import Base

class SourceType(enum.Enum):
    AUDIO = "audio"
    YOUTUBE = "youtube"
    DOCUMENTS = "documents"

class Sources(Base):
    __tablename__ = "sources"
    id:Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),primary_key=True,default=uuid.uuid4
    )
    source_type:Mapped[SourceType] = mapped_column(
        Enum(SourceType,name="source_type"),nullable=False
    )
    source_url:Mapped[str] = mapped_column(String,nullable=True)
    source_name:Mapped[str | None] = mapped_column(String,nullable=True)
    duration:Mapped[str | None] = mapped_column(Integer,nullable=True)
    size:Mapped[int| None] =  mapped_column(Integer,nullable=True)
    user_id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    user = relationship("Users",back_populates="sources")
    notes = relationship("Notes",back_populates="source",cascade="all, delete")
    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
