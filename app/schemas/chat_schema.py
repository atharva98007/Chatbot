from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

class PriorityEnumSchema(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class ChatRequest(BaseModel):
    trip_id: str
    user_id: str
    is_trip_leader: bool = False
    message: str
    trip_context: Dict[str, Any] = Field(
        default_factory=dict,
        example={
            "destination": "Goa",
            "budget": "Moderate",
            "members_count": 5,
            "booked_activities": ["Scuba Diving", "Sunset Cruise"]
        }
    )

class TicketResponse(BaseModel):
    ticket_id: str
    trip_id: str
    raised_by: str
    title: str
    description: str
    priority: str
    status: str

class ChatResponse(BaseModel):
    action: str  # "REPLY" or "TICKET_CREATED"
    reply: str
    ticket: Optional[TicketResponse] = None