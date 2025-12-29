from fastapi import APIRouter, Depends, status
from typing import List

from api.v1.schemas import AppMetadata, AppPermission
from apps.framework.registry import get_registry
from core.deps import get_current_user
from db.postgres import get_pool

router = APIRouter(prefix="/apps", tags=["apps"])


@router.get("", response_model=List[AppMetadata])
async def list_apps():
    """
    List all registered apps with metadata.

    Returns:
        List of app metadata including app_id, display_name, icon, and default_access
    """
    registry = get_registry()
    apps = registry.all()

    return [
        AppMetadata(
            app_id=app.app_id,
            display_name=app.display_name,
            icon=app.icon,
            default_access=app.default_access,
        )
        for app in apps
    ]


@router.get("/permissions", response_model=List[AppPermission])
async def get_my_permissions(current_user: dict = Depends(get_current_user)):
    """
    Get current user's app permissions.

    For each registered app, returns whether the user has access.
    If no explicit permission exists in the database, uses the app's default_access setting.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        List of app permissions with app_id and has_access
    """
    user_id = str(current_user["id"])
    registry = get_registry()
    apps = registry.all()

    # Fetch all explicit permissions for this user
    async with get_pool().acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT app_id, has_access
            FROM user_app_permissions
            WHERE user_id = $1
            """,
            user_id,
        )

    # Build a map of explicit permissions
    explicit_permissions = {row["app_id"]: row["has_access"] for row in rows}

    # For each registered app, use explicit permission if exists, otherwise default_access
    permissions = []
    for app in apps:
        has_access = explicit_permissions.get(app.app_id, app.default_access)
        permissions.append(
            AppPermission(
                app_id=app.app_id,
                has_access=has_access,
            )
        )

    return permissions
