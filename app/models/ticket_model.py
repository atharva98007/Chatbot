import enum
import uuid
from sqlalchemy import Column, String, Text, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database import Base

class PriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class StatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(String, nullable=False, index=True)
    raised_by = Column(String, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.OPEN, nullable=False)
    is_leader_ticket = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)