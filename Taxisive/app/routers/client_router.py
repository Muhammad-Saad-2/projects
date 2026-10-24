import asyncio
import random
import uuid
import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.charge_schema import ChargeRequest

router = APIRouter(prefix="/client", tags=["Client Runner"])

@router.post("/trigger-checkout", summary="Client runner executing retries with backoff & jitter")
async def trigger_checkout(
    payload: ChargeRequest,
    fail_count: int = 2,
    failure_type: str = "server_crash_503"
):
    idem_key = f"req_{uuid.uuid4().hex[:12]}"
    max_retries = 4
    base_delay = 0.5
    max_delay = 4.0
    logs = []

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        for attempt in range(max_retries):
            scenario = failure_type if attempt < fail_count else "normal"
            headers = {
                "Content-Type": "application/json",
                "Idempotency-Key": idem_key
            }

            try:
                resp = await client.post(
                    "/charges",
                    params={"scenario": scenario},
                    headers=headers,
                    json=payload.model_dump()
                )

                logs.append({
                    "attempt": attempt + 1,
                    "status_code": resp.status_code,
                    "cache_header": resp.headers.get("X-Cache-Lookup", "NONE"),
                    "response": resp.json()
                })

                if resp.status_code >= 500:
                    raise httpx.HTTPStatusError("Server error", request=resp.request, response=resp)

                return {
                    "result": "success",
                    "idempotency_key": idem_key,
                    "total_attempts": attempt + 1,
                    "logs": logs,
                    "data": resp.json()
                }

            except (httpx.HTTPStatusError, httpx.RequestError):
                if attempt == max_retries - 1:
                    raise HTTPException(
                        status_code=502,
                        detail={"message": "Max retries exceeded", "logs": logs}
                    )

                # Full Jitter formula: uniform(0, min(max_delay, base * 2^n))
                backoff_cap = min(max_delay, base_delay * (2 ** attempt))
                sleep_duration = random.uniform(0.1, backoff_cap)
                logs[-1]["retry_delay_seconds"] = round(sleep_duration, 3)

                await asyncio.sleep(sleep_duration)