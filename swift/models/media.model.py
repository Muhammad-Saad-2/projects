from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class MediaTypes(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

class Media(SQLModel, table=True):
    id:str = Field(primary_key=True)
    fileUrl:str
    type:MediaTypes = Field(default=MediaTypes.IMAGE)
    created_at:datetime = Field(default=datetime.now())
    updated_at:Optional[datetime] = Field(default=datetime.now())
    tweet_id:str = Field(foreign_key="tweet.id")

class MediaCreate(SQLModel):
    fileUrl:str
    type:MediaTypes
    
