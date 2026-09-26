import json
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from app.config import settings
from app.schemas.chat_schema import ChatRequest, ChatResponse, TicketResponse
from app.services.ticket_service import create_ticket_record

# Initialize Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Tool definition using google-genai SDK types
raise_ticket_tool = types.FunctionDeclaration(
    name="raise_complaint_ticket",
    description="Call this function if the user reports an unresolved issue, payment discrepancy, vendor failure, or explicitly requests support escalation.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "title": types.Schema(
                type="STRING",
                description="Concise headline of the complaint."
            ),
            "description": types.Schema(
                type="STRING",
                description="Detailed explanation of the problem."
            ),
            "suggested_priority": types.Schema(
                type="STRING",
                enum=["LOW", "MEDIUM", "HIGH", "URGENT"],
                description="Urgency level. HIGH or URGENT for financial disputes, booking failures, or safety."
            ),
        },
        required=["title", "description", "suggested_priority"],
    ),
)

tools = types.Tool(function_declarations=[raise_ticket_tool])

def process_chat_query(request: ChatRequest, db: Session) -> ChatResponse:
    # Handle trip_context whether it arrives as a Pydantic object or a dictionary
    if hasattr(request.trip_context, "model_dump"):
        context_dict = request.trip_context.model_dump()
    elif hasattr(request.trip_context, "dict"):
        context_dict = request.trip_context.dict()
    else:
        context_dict = request.trip_context

    system_instruction = f"""
    You are the GroupTrip AI Assistant.
    Your duties:
    1. Provide travel recommendations (restaurants, sights, activities) based on trip context: {json.dumps(context_dict)}.
    2. Answer itinerary, cost split, or vendor-related questions.
    3. Resolve minor issues directly.
    
    CRITICAL RULE:
    If the member experiences an issue you CANNOT resolve directly (such as booking failures, payment disputes, safety issues, or explicit human intervention requests), execute the 'raise_complaint_ticket' tool.
    """

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[tools],
        temperature=0.7,
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=request.message,
            config=config,
        )
    except Exception as e:
        return ChatResponse(
            action="ERROR",
            reply=f"AI service temporarily unavailable: {str(e)}"
        )

    # Check for Function Calls
    if response.function_calls:
        for function_call in response.function_calls:
            if function_call.name == "raise_complaint_ticket":
                args = dict(function_call.args) if function_call.args else {}
                
                ticket_obj = create_ticket_record(
                    db=db,
                    trip_id=request.trip_id,
                    user_id=request.user_id,
                    title=args.get("title", "Issue Reported"),
                    description=args.get("description", "No details provided."),
                    suggested_priority=args.get("suggested_priority", "MEDIUM"),
                    is_trip_leader=request.is_trip_leader
                )

                return ChatResponse(
                    action="TICKET_CREATED",
                    reply=f"I've raised ticket **#{str(ticket_obj.id)[:8]}** for your Trip Leader with priority **{ticket_obj.priority.value}**. Title: {ticket_obj.title}",
                    ticket=TicketResponse(
                        ticket_id=str(ticket_obj.id),
                        trip_id=ticket_obj.trip_id,
                        raised_by=ticket_obj.raised_by,
                        title=ticket_obj.title,
                        description=ticket_obj.description,
                        priority=ticket_obj.priority.value,
                        status=ticket_obj.status.value
                    )
                )

    return ChatResponse(
        action="REPLY",
        reply=response.text if response.text else "How else can I assist your trip?"
    )