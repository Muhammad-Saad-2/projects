from pydantic import BaseModel, EmailStr

#schema for user registration input 
class UserCreate(BaseModel):
    email: EmailStr  #validates email format 
    password : str   # user provided plain text format 

#schema for user data returned in response 
class UserResponse (BaseModel):
    id: int
    email = EmailStr
    role: int #either user or admin

#Aloow SQLalchemy models to integrate with pydantic 
class Config:
    orm_mode = True

