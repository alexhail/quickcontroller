from typing import Optional

from fastapi import APIRouter, Depends, Query

from apps.framework.permissions import require_app_access
from db.postgres import get_pool

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
async def list_audit_logs(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: dict = Depends(require_app_access("command_center")),
):
    """List audit log entries."""
    query = """
        SELECT al.id, al.user_id, u.email as user_email,
               al.action, al.resource_type, al.resource_id,
               al.details, al.ip_address, al.created_at
        FROM cc_audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE 1=1
    """
    params = []
    param_idx = 1

    if action:
        query += f" AND al.action = ${param_idx}"
        params.append(action)
        param_idx += 1

    if user_id:
        query += f" AND al.user_id = ${param_idx}::uuid"
        params.append(user_id)
        param_idx += 1

    query += (
        f" ORDER BY al.created_at DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
    )
    params.extend([limit, offset])

    async with get_pool().acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [dict(row) for row in rows]
