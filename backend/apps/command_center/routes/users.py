from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from apps.framework.permissions import require_app_access
from db.postgres import get_pool

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def list_users(
    current_user: dict = Depends(require_app_access("command_center")),
):
    """List all users."""
    async with get_pool().acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, email, created_at, updated_at FROM users ORDER BY created_at DESC"
        )
    return [dict(row) for row in rows]


@router.get("/{user_id}/app-permissions")
async def get_user_app_permissions(
    user_id: UUID,
    current_user: dict = Depends(require_app_access("command_center")),
):
    """Get app permissions for a specific user."""
    async with get_pool().acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT app_id, has_access, granted_at, granted_by
            FROM user_app_permissions
            WHERE user_id = $1
            """,
            user_id,
        )
    return [dict(row) for row in rows]


@router.put("/{user_id}/app-permissions/{app_id}")
async def set_user_app_permission(
    user_id: UUID,
    app_id: str,
    has_access: bool,
    current_user: dict = Depends(require_app_access("command_center")),
):
    """Set app permission for a user."""
    async with get_pool().acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_app_permissions (user_id, app_id, has_access, granted_by)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id, app_id)
            DO UPDATE SET has_access = $3, granted_by = $4, granted_at = NOW()
            """,
            user_id,
            app_id,
            has_access,
            current_user["id"],
        )
    return {"message": "Permission updated"}
