# app/routers/charges_router.py
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.models.charge_model import Charge
from app.schemas.charge_schema import ChargeCreate, ChargeResponse
from app.services.idempotency_service import get_cache, store_cached_charge

router = APIRouter(prefix="/charges", tags=["Charges"])

@router.post(
    "",
    response_model=ChargeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Charge endpoint with Redis-backed Idempotency"
)
def create_charge(
    payload: ChargeCreate,
    response: Response,
    db: Session = Depends(get_db_session),
    idempotency_key: Annotated[Optional[str], Header(alias="Idempotency-Key")] = None,
    simulate_fail: Optional[bool] = False
):
    # 1. Check Redis Idempotency Ledger
    if idempotency_key:
        cached_result = get_cache(idempotency_key)
        if cached_result:
            # Overwrite the default 201 Created to 200 OK for cached hit
            response.status_code = status.HTTP_200_OK
            response.headers["X-Cache-Lookup"] = "HIT"
            return cached_result

    # 2. Simulate failure (e.g. transient network or DB drop)
    if simulate_fail:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transient database connection glitch."
        )

    # 3. Create real entity in PostgreSQL
    new_charge = Charge(
        id=f"ch_{uuid.uuid4().hex[:10]}",
        amount=payload.amount,
        currency=payload.currency.lower(),
        customer_id=payload.customer_id,
        status="succeeded"
    )
    db.add(new_charge)
    db.commit()
    db.refresh(new_charge)

    # Convert to serializable dict
    result_data = {
        "id": new_charge.id,
        "amount": new_charge.amount,
        "currency": new_charge.currency,
        "customer_id": new_charge.customer_id,
        "status": new_charge.status,
        "created_at": new_charge.created_at.isoformat()
    }

    # 4. Save to Redis with TTL
    if idempotency_key:
        store_cached_charge(idempotency_key, result_data)

    response.headers["X-Cache-Lookup"] = "MISS"
    return result_data