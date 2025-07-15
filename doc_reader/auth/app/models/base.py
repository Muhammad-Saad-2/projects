from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone, timedelta
from typing import Optional

class Base(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        nullable= False
    )
    updated_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate" : lambda : datetime.now(timezone.utc)},
        nullable=False
    
)
class User(Base ,table = True):
    username: str = Field(index = True,unique = True, nullable = False)
    email: str = Field(index = True, unique =True, nullable = False)
    hashed_password : str 
    profile = Relationship(back_populates="user")
    


class Profile(Base, table = True):
    full_name: str = Field(max_length=50, nullable=False)
    bio: str | None = Field(max_length=120)
    user_id: int = Field(foreign_key=True, unique=True)
    user: User = Relationship(back_populates="profile")



    
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
    return Base
