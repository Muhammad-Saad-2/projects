from pydantic import BaseModel, EmailStr
from typing import ClassVar

#schema for user registration input 
class UserCreate(BaseModel):
    email: ClassVar[type] = EmailStr  #validates email format 
    password : str   # user provided plain text format 

#schema for user data returned in response 
class UserResponse (BaseModel):
    id: int
    email : ClassVar[type] = EmailStr
    role: int #either user or admin

#Aloow SQLalchemy models to integrate with pydantic 
class Config:
    orm_mode = True

