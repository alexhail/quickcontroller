from typing import Callable

from fastapi import Depends, HTTPException, status

from apps.framework.registry import get_registry
from core.deps import get_current_user
from db.postgres import get_pool


async def check_app_access(app_id: str, user_id: str) -> bool:
    """
    Check if a user has access to a specific app.

    Access is determined by:
    1. If the app has default_access=True, all authenticated users have access
    2. Otherwise, check the user_app_permissions table for explicit access

    Args:
        app_id: The unique app identifier
        user_id: The user's UUID

    Returns:
        True if the user has access, False otherwise

    Raises:
        KeyError: If the app_id is not registered
    """
    # Get the app to check default_access
    registry = get_registry()
    app = registry.get(app_id)

    # If app has default access, all authenticated users can access it
    if app.default_access:
        return True

    # Check user_app_permissions table for explicit access
    async with get_pool().acquire() as conn:
        result = await conn.fetchval(
            """
            SELECT 1 FROM user_app_permissions
            WHERE user_id = $1 AND app_id = $2
            """,
            user_id,
            app_id,
        )

    return result is not None


def require_app_access(app_id: str) -> Callable:
    """
    FastAPI dependency factory that validates app access.

    Creates a dependency function that checks if the current user
    has access to the specified app. Raises 403 if access is denied.

    Usage:
        @router.get("/data")
        async def get_data(user: dict = Depends(require_app_access("my_app"))):
            ...

    Args:
        app_id: The unique app identifier to check access for

    Returns:
        A FastAPI dependency function that validates access

    Raises:
        HTTPException: 403 Forbidden if the user lacks access
    """

    async def dependency(current_user: dict = Depends(get_current_user)):
        """Dependency that validates app access for the current user."""
        user_id = current_user["id"]

        try:
            has_access = await check_app_access(app_id, user_id)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App '{app_id}' not found",
            )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to app '{app_id}'",
            )

        return current_user

    return dependency
