from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "GroupTrip AI Engine"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    GROUPTRIP_CHATBOT_API_KEY: str
    GEMINI_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()