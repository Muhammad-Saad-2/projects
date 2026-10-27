from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import database
from app.routers.charge_router import router as charges_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        await database.initialize_database()
        yield
    finally:
        engine = database.engine
        if engine is not None:
            await engine.dispose()
            database.engine = None
            database.async_session_maker = None


app = FastAPI(title="Payment Service Prototype", lifespan=lifespan)
app.include_router(charges_router)