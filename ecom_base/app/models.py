#defing the database model 

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class user(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, Index = True)
    email = Column(String, unique=True, Inddex=True, nullable=False )
    hashed_password = Column(String, nullable = False)
    role = Column(String, default="user")