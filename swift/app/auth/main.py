from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_mail import MessageSchema, MessageType, FastMail, ConnectionConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # Import AsyncSession
from sqlalchemy.future import select  # Import select
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel, EmailStr
import random, os
from fastapi.responses import JSONResponse

from ..shared.utils.database import get_async_db, create_table# Import get_async_db and init_db
from ..shared.models.base import User
from ..shared.config.settings import get_settings


settings = get_settings()

load_dotenv()

# Configuring credentials to send the email
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("GOOGLE_EMAIL"),  # Use environment variable for username
    MAIL_PASSWORD=os.getenv("GOOGLE_PASSWORD"),
    MAIL_FROM="hellosaad2002@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="Muhammad Saad",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

app = FastAPI(title="Auth Service")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    otp: dict

# To validate the email format (using a single EmailStr for simplicity in this test)
class EmailSchema(BaseModel):
    email: EmailStr

# Method to generate a random OTP
def generate_otp():
    one_time_password = ""
    for _ in range(6):
        one_time_password += str(random.randint(0, 9))
    return one_time_password

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now() + expires_delta
#     else:
#         expire = datetime.now() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
#     user = await db.query(User).filter(User.username == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
# return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register_email/{email}")
async def send_otp(email: EmailStr) -> JSONResponse:
    try:
        async with get_async_db()as db:
            existing_user = await db.execute(select(User).where(User.email == email))
            existing_user = existing_user.scalars().first()
            if existing_user:
                return {"message": "User already registered"}
            else:
                one_time_password = generate_otp()
                expiration_time = datetime.now() + timedelta(minutes=10)

                new_user = User(
                    username="",
                    email=email,
                    hashed_password="",
                    full_name="",
                    otp={"otp": one_time_password, "expiry": expiration_time.isoformat()}
                )

                db.add(new_user)
                await db.flush()
                await db.commit()

                html = f"""
                <p>Hi,</p>
                <p>Your One-Time Password (OTP) for email verification is:</p>
                <h2>{one_time_password}</h2>
                <p>This OTP will expire in <strong>10 minutes</strong>.</p>
                """

                message = MessageSchema(
                    subject="This is your OTP for Swift",
                    recipients=[email],
                    body=html,
                    subtype=MessageType.html
                )

                fm = FastMail(conf)
                await fm.send_message(message)
                return JSONResponse(status_code=200, content={"message": f"OTP was sent successfully to {email}"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error sending OTP: {str(e)}"})

@app.on_event("startup")
async def startup_event():
    await create_table()

    
@app.post("/verify_otp/{email}/{otp_attempt}")
async def verify_otp(email: EmailStr, otp_attempt:str):

async def register(user_data:UserCreate, db: AsyncSession = Depends(get_async_db)):
    existing_user = await db.execute(select(User).where(User.username == user_data.username))
    exisintg_user = exisintg_user.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,

    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {"message": "User created successfully"}



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)
