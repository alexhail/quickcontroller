import asyncpg

from core.config import settings

pool: asyncpg.Pool | None = None


async def init_pool() -> asyncpg.Pool:
    global pool
    pool = await asyncpg.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database=settings.db_name,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
    )
    return pool


async def close_pool() -> None:
    global pool
    if pool:
        await pool.close()
        pool = None


def get_pool() -> asyncpg.Pool:
    if not pool:
        raise RuntimeError("Database pool not initialized")
    return pool


async def get_connection() -> asyncpg.Connection:
    if not pool:
        raise RuntimeError("Database pool not initialized")
    return await pool.acquire()


async def release_connection(conn: asyncpg.Connection) -> None:
    if pool:
        await pool.release(conn)
