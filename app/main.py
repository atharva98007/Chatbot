from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from app.config import settings
from app.security import verify_api_key
from app.database import get_db, Base, engine
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.llm_service import process_chat_query

# Automatically initialize database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}

@app.post(
    "/api/v1/chat",
    response_model=ChatResponse,
    dependencies=[Depends(verify_api_key)],
    status_code=status.HTTP_200_OK
)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """Main Chat Interface: Process recommendation queries or generate complaint tickets."""
    return process_chat_query(request, db)