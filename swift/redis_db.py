"""Basic connection example.
"""

import redis
import os
from dotenv import load_dotenv

load_dotenv()

r= redis.Redis(
    host=os.getenv ("REDIS_HOST"),
    port=os.getenv ("REDIS_PORT"),
    decode_responses=True,
    username=os.getenv ("REDIS_USERNAME"),
    password=os.getenv("REDIS_PASSWORD"),
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

