
from typing import Annotated
from shared.databases.redis_conn import redis_client
from shared.databases.postgres_conn import async_engine, get_async_session
from auth.app.models.base  import get_base, User
from fastapi import  Depends, HTTPException, APIRouter, status
from auth.app.schemas.auth_schemas import UserCreate, UserLogin, EmailSchema, OtpVerify
from sqlmodel import  select
import asyncio
from auth.app.services.auth_services import hash_password, is_valid_email_regex, run_password_policy, verify_password, generate_otp
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr 
from fastapi.responses import JSONResponse
from fastapi_mail import MessageSchema, MessageType, FastMail
from shared.config.settings import get_settings
from datetime import timedelta
import logging




logger = logging.getLogger("auth.app.routers.auth_router")   
settings = get_settings()
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid Email Pattern"
            )
        password_policy = run_password_policy(user.password)
        if not password_policy:
            
            raise HTTPException(
                status_code=401,
                detail="the password must contain atleast one uppercase, number and a special character"
            )
       
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
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail="user already registered"
        )

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
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED, 
            detail= "incorrect password"
        )
    else:
        return {"message" : "user logged in"}


@router.post("/request_otp/")
async def send_otp(email: EmailStr)-> JSONResponse:
    otp_code = generate_otp()
    otp_expiration_time = timedelta(seconds=900)

    user_email = email
    redis_key = f"otp_for_user: {user_email}"
    try:
        redis_client.set(redis_key, otp_code, ex=otp_expiration_time)
        logger.info("otp stored in redis for {user_email} with key: {redis_key}")
    except Exception as e:
        logger.error("failed to store otp for user {user_email}: {e}", exc_info = True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store OTP, please try again"
        ) 
        

    html = f""" 
    <p> Dear User </p>
    <p>Your One-time-password is </p>
    <h2>{otp_code}</h2>
    <p>It will expire in 15 minutes
    
    """

    message = MessageSchema(
        subject="One-Time-Password-Verification",
        recipients=[user_email],
        body=html, 
        subtype=MessageType.html

    )
    fm = FastMail(settings.email_conf)

    await fm.send_message(message)
    return JSONResponse(status_code= 200, content={"message" : f"OTP was successfully sent to {email}"})



@router.post("/verify_otp/")
async def verify_otp(
    otp_data: OtpVerify,
    session: SessionDep
):
    user_email = otp_data.email
    otp_attempt = otp_data.otp_code

    redis_key = f"otp_for_user: {user_email}"
    try:
        stored_otp= redis_client.get(redis_key)
        if stored_otp is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP or perhaps the OTP expired"
            )
        
        stored_otp_in_str = stored_otp.decode("utf-8")

        if otp_attempt == stored_otp_in_str:
            await redis_client.delete(redis_key)
            logger.info("OTP successfully verfied for user {user_email} and deleted from redis")

            return JSONResponse(status_code=200, content= {"message": "OTP verified successfully"})
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
    except HTTPException:
        raise

    except Exception as e:
        logger.error("Error during otp verification for {user_email}: {e}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured while verifying the user {user_email}"
        )
        

    
    

    '''get email from the database
        get otp from redis 
        save the user attempted otp in a variable
        write an if condition if email and otp matches 
        if 
            any of them is false or otp timed out
            raise the error 
        else:
            delete the otp from the db 
            success message print karwad'''

    

    

@router.put("/forget_password")
async def reset_password(email: EmailStr):
    pass 


