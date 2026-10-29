# client/checkout_client.py
import random
import time
import uuid
import httpx

SERVER_URL = "http://127.0.0.1:8000/charges"

def run_checkout_flow():
    # Generate a single Idempotency Key for this checkout attempt session
    idem_key = f"req_{uuid.uuid4().hex[:12]}"

    payload = {
        "amount": 9999,  # $99.99
        "currency": "usd",
        "customer_id": "cust_jane_smith"
    }

    max_retries = 4
    base_delay = 0.5
    max_delay = 4.0

    print("=" * 60)
    print(f"CHECKOUT INITIATED | Generated Idempotency-Key: {idem_key}")
    print("=" * 60)

    for attempt in range(max_retries):
        # We simulate failures on the first 2 attempts, then let it succeed
        simulate_failure = attempt < 2

        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": idem_key
        }
        params = {"simulate_fail": simulate_failure}

        print(f"\n[Attempt #{attempt + 1}] Sending POST request to server...")

        try:
            with httpx.Client() as client:
                res = client.post(SERVER_URL, json=payload, headers=headers, params=params)

            # If server returns a 5xx error, raise to trigger retry block
            if res.status_code >= 500:
                print(f"❌ Server Error [{res.status_code}]: {res.json().get('detail')}")
                raise httpx.HTTPStatusError("Server error", request=res.request, response=res)

            # Success!
            cache_lookup = res.headers.get("X-Cache-Lookup", "NONE")
            print(f"✅ Success! Status: {res.status_code} | Cache Lookup: {cache_lookup}")
            print(f"   Response Body: {res.json()}")
            return res.json()

        except (httpx.HTTPStatusError, httpx.RequestError):
            if attempt == max_retries - 1:
                print("💥 Max retries exhausted. Checkout failed.")
                raise

            # --- BACKOFF & JITTER CALCULATION ---
            backoff_cap = min(max_delay, base_delay * (2 ** attempt))
            jittered_sleep = random.uniform(0.1, backoff_cap)

            print(f"⏳ Backoff Cap: {backoff_cap:.2f}s | Jittered Sleep: {jittered_sleep:.2f}s")
            time.sleep(jittered_sleep)

if __name__ == "__main__":
    run_checkout_flow()