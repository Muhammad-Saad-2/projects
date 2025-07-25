from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from functools import lru_cache
from fastapi_mail import ConnectionConfig
import os
from typing import ClassVar




load_dotenv()

class Settings(BaseSettings):
    # Database URLs
    MONGODB_URL:str  = os.getenv("MONGODB_URL", "")
    POSTGRES_URL:str  = os.getenv("POSTGRES_URL", "")
    REDIS_HOST:str  = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 19437 ))
    REDIS_USERNAME:str  = os.getenv("REDIS_USERNAME", "")
    REDIS_PASSWORD:str  = os.getenv("REDIS_PASSWORD", "")


    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Settings

    email_conf:ClassVar[ConnectionConfig] = ConnectionConfig(
        MAIL_USERNAME= os.getenv("GOOGLE_EMAIL", ""),
        MAIL_PASSWORD=os.getenv("GOOGLE_PASSWORD", ""),
        MAIL_FROM=os.getenv("SENDER_MAIL"),
        MAIL_FROM_NAME= "Muhammad Saad",
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,

    )


    '''extra = "ignore" because pydantic encountered an extra environmental variable from my .env file (google_api_key) since my Settings model did not
    not have any corresponding field defined for that environmnetal variable '''
    
    model_config = SettingsConfigDict(env_file= ".env", extra="ignore")


                                                                        
@lru_cache(maxsize=100)
def get_settings():
    return Settings()


