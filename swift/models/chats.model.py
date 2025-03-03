from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Chat(SQLModel, table=True):
    id:str = Field(primary_key=True)
    content:str
    message_id:str = Field(foreign_key="message.id")
    sender_id:str = Field(foreign_key="user.id")
    receiver_id:str = Field(foreign_key="user.id")
    is_read:bool = Field(default=False)
    created_at:datetime = Field(default=datetime.now())
    updated_at:Optional[datetime] = Field(default=datetime.now())

class ChatCreate(SQLModel):
    content:str
    message_id:str
    sender_id:str
    receiver_id:str
