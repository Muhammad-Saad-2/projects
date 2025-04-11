from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

class Settings(BaseSettings):
    # Database URLs
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")


    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    POSTS_SERVICE_URL: str = "http://localhost:8002"
    NOTIFICATIONS_SERVICE_URL: str = "http://localhost:8003"
    USERS_SERVICE_URL: str = "http://localhost:8004"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 