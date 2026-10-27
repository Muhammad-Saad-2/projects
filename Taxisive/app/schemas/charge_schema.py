import datetime
from pydantic import BaseModel, Field

class ChargeCreate(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in cents (e.g. 2500 = $25.00)")
    currency: str = Field(default="usd", min_length=3, max_length=3)
    customer_id: str

class ChargeResponse(BaseModel):
    id: str
    amount: int
    currency: str
    customer_id: str
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True