from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from redis_db import r
load_dotenv()

class Settings(BaseSettings):
    # Database URLs
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")
    REDIS_URL = r


    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    POSTS_SERVICE_URL: str = "http://localhost:8002"
    NOTIFICATIONS_SERVICE_URL: str = "http://localhost:8003"
    USERS_SERVICE_URL: str = "http://localhost:8004"

    
    class Config:
        env_file = ".env"

@lru_cache(maxsize = 5)
def get_settings():
    return Settings() 