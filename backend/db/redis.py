import redis.asyncio as redis

from core.config import settings

client: redis.Redis | None = None


async def init_redis() -> redis.Redis:
    global client
    client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )
    await client.ping()
    return client


async def close_redis() -> None:
    global client
    if client:
        await client.close()
        client = None


def get_redis() -> redis.Redis:
    if not client:
        raise RuntimeError("Redis client not initialized")
    return client
