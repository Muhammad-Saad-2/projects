from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Follow(SQLModel, table=True):
    id:str = Field(primary_key=True)
    follower_id:str = Field(foreign_key="user.id")
    following_id:str = Field(foreign_key="user.id")
    created_at:datetime = Field(default=datetime.now())
    updated_at:Optional[datetime] = Field(default=datetime.now())

class FollowCreate(SQLModel):
    follower_id:str
    following_id:str
