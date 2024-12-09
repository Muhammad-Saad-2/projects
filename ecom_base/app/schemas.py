from pydantic import BaseModel, EmailStr


#schema for user registration input 
class UserCreate(BaseModel):
    email: EmailStr  #validates email format 
    password : str   # user provided plain text format 

#schema for user data returned in response 
class UserResponse (BaseModel):
    id: int
    email : EmailStr
    role: str #either user or admin

class UserLogin(BaseModel):
    email : EmailStr # ensuring that the email is valid
    password:  str #plain text password for login

class TokeN(BaseModel):
    access_token : str
    token_type : str 

#Aloow SQLalchemy models to integrate with pydantic 
class Config:
    orm_mode = True

