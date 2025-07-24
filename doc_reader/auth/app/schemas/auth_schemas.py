from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import List


class UserCreate(SQLModel): # Removed 'User' from inheritance, and removed 'table=True'
    username: str = Field(max_length=50, nullable=False)
    email: EmailStr= Field(max_length=100, nullable=False)
    password: str = Field(min_length=8, max_length=256, nullable=False) # Changed max_length for password
    # You might add a password_confirm: str field for validation if needed


class EmailSchema(SQLModel):
    email: List[EmailStr] = Field(max_length=50, unique=True, index= True)


class UserLogin(SQLModel):
    email: EmailStr = Field(max_length=50, nullable=False)
    password: str = Field(min_length=8, max_length=25, nullable= False)

