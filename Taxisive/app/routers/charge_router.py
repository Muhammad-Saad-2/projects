import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.charge_model import Charge
from app.schemas.charge_schema import ChargeRequest, ChargeResponse

router = APIRouter(prefix="/charges", tags=["Charges"])


def _charge_response(charge: Charge) -> ChargeResponse:
    return ChargeResponse(
        id=charge.id,
        amount=charge.amount,
        currency=charge.currency,
        customer=charge.customer_id,
        status=charge.status,
    )


@router.post(
    "",
    response_model=ChargeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a charge with idempotency support",
)
async def create_charge(
    payload: ChargeRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    scenario: str = "normal",
):
    idempotency_key = idempotency_key or None

    if idempotency_key:
        existing_charge = await session.scalar(
            select(Charge).where(Charge.idempotency_key == idempotency_key)
        )
        if existing_charge is not None:
            response.status_code = status.HTTP_200_OK
            response.headers["X-Cache-Lookup"] = "HIT"
            return _charge_response(existing_charge)

    if scenario == "server_crash_503":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection pool exhausted"
        )

    if scenario == "connection_drop":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulated network dropped before response dispatch",
        )

    charge = Charge(
        id=f"ch_{uuid.uuid4().hex[:8]}",
        amount=payload.amount,
        currency=payload.currency,
        customer_id=payload.customer_id,
        status="succeeded",
        idempotency_key=idempotency_key,
    )
    session.add(charge)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        if not idempotency_key:
            raise

        existing_charge = await session.scalar(
            select(Charge).where(Charge.idempotency_key == idempotency_key)
        )
        if existing_charge is None:
            raise

        response.status_code = status.HTTP_200_OK
        response.headers["X-Cache-Lookup"] = "HIT"
        return _charge_response(existing_charge)

    response.headers["X-Cache-Lookup"] = "MISS"
    return _charge_response(charge)