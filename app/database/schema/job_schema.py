import enum
import uuid
from datetime import datetime ,timezone
from sqlalchemy import Boolean,DateTime,Enum, ForeignKey,String,Integer
from sqlalchemy.orm import Mapped,mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from ..db import Base

class JobStatusEnum(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"

class JobTypeEnum(enum.Enum):
    AUDIO = "audio"
    YOUTUBE = "youtube"
    DOCUMENTS = "documents"


class Jobs(Base):
    __tablename__="jobs"
    id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    source_id :Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id"),
        nullable=False
    )
    job_type:Mapped[JobTypeEnum] = mapped_column(
        Enum(JobTypeEnum,name="job_type_enum"),
        nullable=False
    )
    job_status:Mapped[JobStatusEnum]=mapped_column(
        Enum(JobStatusEnum,name="job_status_enum"),
        nullable=False
    )
    progress:Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    current_step:Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    error_info:Mapped[str |None] = mapped_column(
        String,
        nullable=True
    )
    retry_count :Mapped[int |None] = mapped_column(
        Integer,
        nullable=True
    )
    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        nullable=False
    )
    updated_at:Mapped[datetime]= mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc),
        nullable=False
    )
    source = relationship("Sources",back_populates="jobs")
