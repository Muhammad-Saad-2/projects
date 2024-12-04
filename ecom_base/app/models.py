#defing the database model 

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index = True)
    email = Column(String, unique=True, index=True, nullable=False )
    hashed_password = Column(String, nullable = False)
    role = Column(String, default="user")