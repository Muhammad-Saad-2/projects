# app/models/charge_model.py
import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.core.database import Base

class Charge(Base):
    __tablename__ = "charges"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)        # In cents: 5000 = $50.00
    currency = Column(String(3), nullable=False)    # e.g., 'usd'
    customer_id = Column(String, nullable=False, index=True)
    status = Column(String, default="succeeded")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)