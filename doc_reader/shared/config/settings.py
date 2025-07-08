from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache
import os 


load_dotenv()

class Settings(BaseSettings):
    # Database URLs
    MONGODB_URL:str  = os.getenv("MONGODB_URL", "")
    POSTGRES_URL:str  = os.getenv("POSTGRES_URL", "")
    REDIS_HOST:str  = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 13582 ))
    REDIS_USERNAME:str  = os.getenv("REDIS_USERNAME", "")
    REDIS_PASSWORD:str  = os.getenv("REDIS_PASSWORD", "")

   
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Settings
    GOOGLE_EMAIL: str = os.getenv("GOOGLE_EMAIL", "")
    GOOGLE_PASSWORD: str = os.getenv("GOOGLE_PASSWORD", "")

    class Config:
        env_file = ".env"

@lru_cache(maxsize=100)
def get_settings():
    return Settings()

