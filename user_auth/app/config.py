from pydantic_settings import BaseSettings
from starlette.config import Config
from starlette.datastructures import Secret


try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()


class Settings(BaseSettings):
    DATABASE_URL: str=config("DATABASE_URL", cast=Secret)
    SECRET_KEY:str =config("SECRET_KEY", cast=Secret)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


    class Config:
        env_file = ".env" 
        extra = "allow"

settings = Settings()






