from sqlmodel import create_engine, SQLModel
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_URL")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def db_init():
    SQLModel.metadata.create_all(engine)

def get_session():
    with SessionLocal() as session:
        yield session

