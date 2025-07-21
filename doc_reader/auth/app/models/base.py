from sqlmodel import SQLModel, Field
from datetime import datetime
from shared.config.settings import get_settings
from pydantic import EmailStr, ConfigDict
from sqlalchemy import func


settings = get_settings()
POSTGRES_URL = settings.POSTGRES_URL

class Base(SQLModel):
    id: int = Field(primary_key=True, default= None)
    created_at: datetime = Field(default_factory=func.now)
    updated_at: datetime = Field(
        default_factory=func.now, 
        sa_column_kwargs={
            "onupdate": func.now()
            }
        )


class User(Base,table = True):
    username: str = Field(index = True,unique = True, nullable = False)
    email: EmailStr = Field(index = True, unique =True, nullable = False)
    hashed_password : str 
    # profile = Relationship(back_populates="user")
    


class Profile(Base, table=True):
    full_name: str = Field(max_length=50, nullable=False)
    username: str = Field(unique=True, max_length= 50 )
    bio: str | None = Field(max_length=120)
    user_id: int = Field(foreign_key="user.id")
    # user: User = Relationship(back_populates="profile")


    
# class OTP(Base, table = True ):
#     otp_code: str = Field(index=True)

#     expires_at: datetime = Field(
#         default_factory=lambda:datetime.now(timezone.utc) + timedelta(minutes=15),
#         nullable=False
#     )
#     is_used : bool = Field(default=False)
#     user_id: int = Field(foreign_key="user.id", index=True)
#     user: User = Relationship(back_populates="otps")
#     otp_id: int = Field(primary_key=True, index=True, unique=True)




def get_base():
    return Base()
