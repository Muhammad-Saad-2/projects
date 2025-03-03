from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Tweet(SQLModel, table=True):
    id: str = Field(primary_key=True)
    content: str
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=datetime.now())
    userId: str = Field(foreign_key="user.id")

class TweetCreate(SQLModel):
    content: str
    userId: str
