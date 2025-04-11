from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from ..config.settings import get_settings
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

settings = get_settings()

# PostgreSQL setup
SQLALCHEMY_DATABASE_URL = settings.POSTGRES_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB setup
mongodb_client = MongoClient(settings.MONGODB_URL, server_api=ServerApi('1'))
mongodb = mongodb_client.get_database("twitter_clone")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 