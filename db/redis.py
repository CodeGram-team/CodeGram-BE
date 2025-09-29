import redis.asyncio as redis
from dotenv import load_dotenv
import os
load_dotenv()

REDIS_URL=os.getenv("REDIS_URL")

redis_client = redis.from_url(
    REDIS_URL,
    decode_response=True
)
async def get_redis_client():
    return redis_client

