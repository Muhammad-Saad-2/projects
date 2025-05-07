from sqlmodel  import SQLModel, create_engine, Session
from sqlmodel import SQLModel
from ..config.settings import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


settings = get_settings()

# PostgreSQL setup
PGSQL_DATABASE_URL = settings.POSTGRES_URL
engine = create_engine(PGSQL_DATABASE_URL)
SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)
Base = SQLModel()

# MongoDB setup
mongodb_client= AsyncIOMotorClient(settings.MONGODB_URL, server_api = ServerApi('1'))
mongodb = mongodb_client.get_database("swift")

# #Redis Setup
redis_client = settings.REDIS_URL



# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 