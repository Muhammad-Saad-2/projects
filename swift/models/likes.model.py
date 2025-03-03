from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Like(SQLModel, table=True):
    id:str = Field(primary_key=True)
    created_at:datetime = Field(default=datetime.now())
    user_id:str = Field(foreign_key="user.id")
    tweet_id:str = Field(foreign_key="tweet.id")

class LikeCreate(SQLModel):
    user_id:str
    tweet_id:str

