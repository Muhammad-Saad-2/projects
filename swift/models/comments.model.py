from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Comment(SQLModel, table=True):
    id:str = Field(primary_key=True)
    content:str
    created_at:datetime = Field(default=datetime.now())
    updated_at:Optional[datetime] = Field(default=datetime.now())
    user_id:str = Field(foreign_key="user.id")
    tweet_id:str = Field(foreign_key="tweet.id")

class CommentCreate(SQLModel):
    content:str
    user_id:str 
    tweet_id:str 
