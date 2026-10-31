import json
from app.core.database import redis_client

IDEMPOTENCY_TTL_SECONDS = 86400

async def get_cache(idem_key:str):
    cached_data = await redis_client.get(f"idem:{idem_key}")
    if cached_data:
        return  json.loads(cached_data)
    return None

async def store_cached_charge(idem_key: str, charge_dict: dict) -> None:
    """
    Stores the serialized response in Redis with an auto-expiring TTL.
    """
    await redis_client.setex(
        name=f"idem:{idem_key}",
        time=IDEMPOTENCY_TTL_SECONDS,
        value=json.dumps(charge_dict, default=str)
    )