
from typing import Annotated
from shared.databases.postgres_conn import async_engine, get_async_session, create_table
from auth.app.models.base  import get_base, User
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from auth.app.schemas.user_schemas import UserCreate, UserLogin
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import asyncio
from auth.app.services.utilities import hash_password, is_valid_email_regex, run_password_policy, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr 

base = get_base()
engine = async_engine 
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/sign_up/", response_model = User)
async def register_user(
    user: UserCreate,
    session: SessionDep,
):
    query = select(User).where(User.email == user.email)
    existing_user_result = await session.execute(query)  #scalar() method is only called on executed object
    existing_user = existing_user_result.scalars().first()
    if not existing_user:
        regex_check_on_email = is_valid_email_regex(user.email)
        if not regex_check_on_email:
            raise HTTPException(status_code=401,detail="Invalid Email Pattern")
        password_policy = run_password_policy(user.password)
        if not password_policy:
            
            raise HTTPException(status_code=401,detail="the password must contain atleast one uppercase, number and a special character")
       
        password = hash_password(user.password)
        db_user = User(
            username = user.username,
            email=user.email,
            hashed_password=password
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        print("your account has been registered")
        return db_user
    
    else:
        raise HTTPException(status_code=401, detail="user already registered")


@router.post("/sign_in/")
async def login(
    user: UserLogin,
    session: SessionDep
):
    query= select(User).where(User.email == user.email)
    registered_user_result = await session.execute(query)
    registered_user = registered_user_result.scalars().first()
    if not registered_user:
        raise HTTPException(status_code = 401, detail = "unauthorized access, please regsiter yourself first")
    user_password = user.password
    db_password = registered_user.hashed_password
    password_match =verify_password(user_password, db_password)
    if not password_match:
        raise HTTPException(status_code= 401, detail= "incorrect password")
    else:
        return {"message" : "user logged in"}

@router.put("/forget_password")
async def reset_password(email: EmailStr):
    pass 


@router.post("/verfiy_email")
async def send_otp(email: EmailStr):
    pass 




