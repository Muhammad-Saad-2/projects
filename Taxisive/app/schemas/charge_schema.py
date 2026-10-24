from pydantic import BaseModel, Field

class ChargeRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in cents (e.g. 4999 = $49.99)")
    currency: str = Field(default="usd", min_length=3, max_length=3)
    customer_id: str

class ChargeResponse(BaseModel):
    id: str
    amount: int
    currency: str
    customer: str
    status: str