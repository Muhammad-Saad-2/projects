from sqlmodel import SQLModel, Field, Date
from pydantic import EmailStr
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    first_name: str
    last_name: str
    year_of_birth: int
    month_of_birth: int
    username: str = Field(unique=True)
    email : EmailStr = Field(unique=True, nullable=False)
    password : str 
    bio: Optional[str] = None 
    profile_picture: Optional[str] = None
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=datetime.now())
    verified: bool = False
    status: str = Field(default="active")

class UserCreate(SQLModel):
    first_name : str
    last_name: str
    dob : Date
    username: str
    email : EmailStr 
    password : str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

