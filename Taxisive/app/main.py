from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import database
from app.core.database import get_db_session
from app.models.charge_model import Charge
from app.routers import charge_router, client_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.initialize_database()
    app.state.async_session_maker = database.async_session_maker
    yield
    if database.engine is not None:
        await database.engine.dispose()


app = FastAPI(
    title="Idempotency & Resilience API",
    description="Demonstrates Idempotent APIs with Exponential Backoff and Full Jitter.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register sub-routers
app.include_router(charge_router.router)
app.include_router(client_router.router)

@app.get("/admin/db-state", tags=["Admin"])
async def inspect_database(
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """Inspect committed charges and the active idempotency ledger."""
    charges = (
        await session.scalars(select(Charge).order_by(Charge.id))
    ).all()
    return {
        "charges_committed_count": len(charges),
        "charges": [
            {
                "id": charge.id,
                "amount": charge.amount,
                "currency": charge.currency,
                "customer": charge.customer_id,
                "status": charge.status,
            }
            for charge in charges
        ],
        "cached_idempotency_keys": [
            charge.idempotency_key
            for charge in charges
            if charge.idempotency_key is not None
        ],
    }