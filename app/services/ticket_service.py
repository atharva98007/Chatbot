from sqlalchemy.orm import Session
from app.models.ticket_model import Ticket, PriorityEnum, StatusEnum

def create_ticket_record(
    db: Session,
    trip_id: str,
    user_id: str,
    title: str,
    description: str,
    suggested_priority: str,
    is_trip_leader: bool
) -> Ticket:
    """Applies leader prioritization logic and persists ticket into DB."""
    # Prioritization logic: Leader claims or issues carry higher weight
    if is_trip_leader:
        final_priority = PriorityEnum.URGENT if suggested_priority in ["HIGH", "URGENT"] else PriorityEnum.HIGH
    else:
        final_priority = PriorityEnum(suggested_priority)

    db_ticket = Ticket(
        trip_id=trip_id,
        raised_by=user_id,
        title=title,
        description=description,
        priority=final_priority,
        status=StatusEnum.OPEN,
        is_leader_ticket=is_trip_leader
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket