from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from datetime import timedelta

class SubscriptionTypes(str, Enum):
    FREE = "basic "
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Subscription(SQLModel, table=True):
    id:str = Field(primary_key=True)
    subscription_type:SubscriptionTypes = Field(default=SubscriptionTypes.FREE)
    startDate:datetime = Field(default=datetime.now())
    updated_at:Optional[datetime] = Field(default=datetime.now())
    end_date:datetime = Field(default=datetime.now() + timedelta(days=30))
    user_id:str = Field(foreign_key=True)


class SubscriptionCreate(SQLModel):
    subscription_type:SubscriptionTypes
    startDate:datetime
    end_date:datetime
    user_id:str 

