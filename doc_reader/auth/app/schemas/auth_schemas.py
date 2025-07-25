# from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from typing import List
from pydantic import BaseModel, Field


class UserCreate(BaseModel): # Removed 'User' from inheritance, and removed 'table=True'
    username: str = Field(max_length=50)
    email: EmailStr= Field(max_length=120)
    password: str = Field(min_length=8, max_length=25) # Changed max_length for password
    # You might add a password_confirm: str field for validation if needed


class EmailSchema(BaseModel):
    email: List[EmailStr] = Field(max_length=50)


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=50)
    password: str = Field(min_length=8, max_length=25,)


class OtpVerify(BaseModel):
    email: EmailStr = Field(max_length=50)
    otp_code : str 

