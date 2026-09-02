import os

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True
    )