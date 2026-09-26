from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verifies that incoming REST calls present the correct API Key header."""
    if api_key != settings.GROUPTRIP_CHATBOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing X-API-Key header"
        )
    return api_key