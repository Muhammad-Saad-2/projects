from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os 
from dotenv import load_dotenv

load_dotenv()

#connection string to pgsql database 
database_url = os.getenv("DATABASE_URL")

if database_url:
    print("yes")
else:
    print("no")
#creating the database engine 
engine = create_engine(database_url)

#creating the database session 
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

#dependency for opening a database session 
def get_db():
    db = SessionLocal() #open a session 
    try:
        yield db #provide the session to the caller  
    finally:
        db.close() #close the database connection 