from sqlmodel import SQLModel, Field
from datetime import datetime
from shared.config.settings import get_settings
from pydantic import EmailStr, ConfigDict
from sqlalchemy import func


settings = get_settings()
POSTGRES_URL = settings.POSTGRES_URL

class Base(SQLModel):
    id: int = Field(primary_key=True, default= None)
    created_at: datetime = Field(
        default_factory=func.now
        )
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
    verified_user: bool = Field(default=False, nullable=False)

    


class Profile(Base, table=True):
    full_name: str = Field(max_length=50, nullable=False)
    username: str = Field(unique=True, max_length= 50 )
    bio: str | None = Field(max_length=120)
    user_id: int = Field(foreign_key="user.id")




def get_base():
    return Base()
