from fastapi import APIRouter, Depends

from apps.framework.permissions import require_app_access
from apps.framework.registry import get_registry
from db.postgres import get_pool
from db.redis import get_redis

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health")
async def system_health(
    current_user: dict = Depends(require_app_access("command_center")),
):
    """Get system health status."""
    health = {"database": "unknown", "redis": "unknown", "apps": []}

    try:
        async with get_pool().acquire() as conn:
            await conn.fetchval("SELECT 1")
        health["database"] = "healthy"
    except Exception as e:
        health["database"] = f"error: {str(e)}"

    try:
        redis = get_redis()
        await redis.ping()
        health["redis"] = "healthy"
    except Exception as e:
        health["redis"] = f"error: {str(e)}"

    registry = get_registry()
    health["apps"] = [
        {"app_id": app.app_id, "display_name": app.display_name}
        for app in registry.all()
    ]

    return health


@router.get("/stats")
async def system_stats(
    current_user: dict = Depends(require_app_access("command_center")),
):
    """Get system statistics."""
    async with get_pool().acquire() as conn:
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        controller_count = await conn.fetchval(
            "SELECT COUNT(*) FROM master_controllers"
        )
        online_controllers = await conn.fetchval(
            "SELECT COUNT(*) FROM master_controllers WHERE connection_status = 'online'"
        )

    return {
        "users": {"total": user_count},
        "controllers": {
            "total": controller_count,
            "online": online_controllers,
            "offline": controller_count - online_controllers,
        },
    }
