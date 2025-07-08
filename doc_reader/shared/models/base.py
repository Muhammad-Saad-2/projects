from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

class Base(SQLModel):
    pass 

class User(Base ,table = True):
    id: int | None = Field(default = None, primary_key = True)
    username: str = Field(index = True,unique = True, nullable = False)
    email: str = Field(index = True, unique =True, nullable = False)
    password: str 
    is_active: bool = Field(default = True)

    created_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        nullable= False
    )
    updated_at: datetime = Field(
        default_factory=lambda:datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate" : lambda : datetime.now(timezone.utc)},
        nullable=False
)
    verified_user: bool = Field(default=False)

class Profile(Base, table = True):
    full_name: str = Field(max_length=50, nullable=False)
    bio: str | None = Field(max_length=120)
    user_id: int = Field(foreign_key="user.id", unique=True)
    user: User = Relationship(back_populates="profile")