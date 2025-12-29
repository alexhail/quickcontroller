from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.v1.schemas import (
    ControllerCreate,
    ControllerResponse,
    ControllerUpdate,
    DiscoveredController,
    EntityState,
    MessageResponse,
    TestConnectionRequest,
    TestConnectionResponse,
)
from apps.discovery import discover_home_assistant
from apps.ha_client import HomeAssistantClient, test_ha_connection
from apps.framework.permissions import require_app_access
from core.encryption import decrypt_token, encrypt_token
from db.postgres import get_pool

router = APIRouter(prefix="/controllers", tags=["controllers"])


def _row_to_controller(row: dict) -> ControllerResponse:
    """Convert database row to ControllerResponse."""
    return ControllerResponse(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        name=row["name"],
        url=row["url"],
        connection_status=row["connection_status"],
        last_seen=row["last_seen"],
        last_error=row["last_error"],
        ha_version=row["ha_version"],
        discovered_via=row["discovered_via"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@router.get("", response_model=List[ControllerResponse])
async def list_controllers(current_user: dict = Depends(require_app_access("command_center"))):
    """List all controllers for the current user."""
    async with get_pool().acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, user_id, name, url, connection_status, last_seen,
                   last_error, ha_version, discovered_via, created_at, updated_at
            FROM master_controllers
            WHERE user_id = $1
            ORDER BY created_at DESC
            """,
            current_user["id"],
        )

    return [_row_to_controller(row) for row in rows]


@router.get("/{controller_id}", response_model=ControllerResponse)
async def get_controller(controller_id: UUID, current_user: dict = Depends(require_app_access("command_center"))):
    """Get a specific controller by ID."""
    async with get_pool().acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, user_id, name, url, connection_status, last_seen,
                   last_error, ha_version, discovered_via, created_at, updated_at
            FROM master_controllers
            WHERE id = $1 AND user_id = $2
            """,
            controller_id,
            current_user["id"],
        )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Controller not found",
        )

    return _row_to_controller(row)


@router.post("", response_model=ControllerResponse, status_code=status.HTTP_201_CREATED)
async def create_controller(
    data: ControllerCreate, current_user: dict = Depends(require_app_access("command_center"))
):
    """Create a new controller."""
    # Test connection before saving
    success, error, version = await test_ha_connection(data.url, data.access_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect to Home Assistant: {error}",
        )

    # Encrypt the access token
    encrypted_token = encrypt_token(data.access_token)

    async with get_pool().acquire() as conn:
        # Check for duplicate URL for this user
        existing = await conn.fetchrow(
            "SELECT id FROM master_controllers WHERE user_id = $1 AND url = $2",
            current_user["id"],
            data.url,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A controller with this URL already exists",
            )

        # Insert the new controller
        row = await conn.fetchrow(
            """
            INSERT INTO master_controllers
                (user_id, name, url, access_token_encrypted, connection_status,
                 last_seen, ha_version, discovered_via)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, user_id, name, url, connection_status, last_seen,
                      last_error, ha_version, discovered_via, created_at, updated_at
            """,
            current_user["id"],
            data.name,
            data.url,
            encrypted_token,
            "online",
            datetime.utcnow(),
            version,
            data.discovered_via,
        )

    return _row_to_controller(row)


@router.patch("/{controller_id}", response_model=ControllerResponse)
async def update_controller(
    controller_id: UUID, data: ControllerUpdate, current_user: dict = Depends(require_app_access("command_center"))
):
    """Update a controller."""
    async with get_pool().acquire() as conn:
        # Verify ownership
        existing = await conn.fetchrow(
            "SELECT id FROM master_controllers WHERE id = $1 AND user_id = $2",
            controller_id,
            current_user["id"],
        )

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Controller not found",
            )

        # Build update query dynamically
        updates = []
        values = []
        param_count = 1

        if data.name is not None:
            updates.append(f"name = ${param_count}")
            values.append(data.name)
            param_count += 1

        if data.url is not None:
            updates.append(f"url = ${param_count}")
            values.append(data.url)
            param_count += 1

        if data.access_token is not None:
            encrypted_token = encrypt_token(data.access_token)
            updates.append(f"access_token_encrypted = ${param_count}")
            values.append(encrypted_token)
            param_count += 1

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        # Add updated_at
        updates.append(f"updated_at = ${param_count}")
        values.append(datetime.utcnow())
        param_count += 1

        # Add controller_id for WHERE clause
        values.append(controller_id)

        query = f"""
            UPDATE master_controllers
            SET {', '.join(updates)}
            WHERE id = ${param_count}
            RETURNING id, user_id, name, url, connection_status, last_seen,
                      last_error, ha_version, discovered_via, created_at, updated_at
        """

        row = await conn.fetchrow(query, *values)

    return _row_to_controller(row)


@router.delete("/{controller_id}", response_model=MessageResponse)
async def delete_controller(controller_id: UUID, current_user: dict = Depends(require_app_access("command_center"))):
    """Delete a controller."""
    async with get_pool().acquire() as conn:
        result = await conn.execute(
            "DELETE FROM master_controllers WHERE id = $1 AND user_id = $2",
            controller_id,
            current_user["id"],
        )

    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Controller not found",
        )

    return MessageResponse(message="Controller deleted successfully")


@router.post("/discover", response_model=List[DiscoveredController])
async def discover_controllers(current_user: dict = Depends(require_app_access("command_center"))):
    """Discover Home Assistant instances on the local network."""
    discovered = await discover_home_assistant(timeout=5)
    return discovered


@router.post("/test-connection", response_model=TestConnectionResponse)
async def test_connection(data: TestConnectionRequest, current_user: dict = Depends(require_app_access("command_center"))):
    """Test connection to a Home Assistant instance."""
    success, error, version = await test_ha_connection(data.url, data.access_token)

    return TestConnectionResponse(success=success, error=error, version=version)


@router.get("/{controller_id}/entities", response_model=List[EntityState])
async def get_controller_entities(
    controller_id: UUID,
    domain: Optional[str] = None,
    current_user: dict = Depends(require_app_access("command_center"))
):
    """Get all entities from a controller, optionally filtered by domain."""
    async with get_pool().acquire() as conn:
        # Verify ownership and get controller details
        row = await conn.fetchrow(
            """
            SELECT url, access_token_encrypted, connection_status
            FROM master_controllers
            WHERE id = $1 AND user_id = $2
            """,
            controller_id,
            current_user["id"],
        )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Controller not found",
        )

    # Decrypt the access token
    access_token = decrypt_token(row["access_token_encrypted"])

    # Create HA client and fetch states
    ha_client = HomeAssistantClient(row["url"], access_token)
    states = await ha_client.get_states()

    if states is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to fetch entities from Home Assistant",
        )

    # Process and format entities
    entities = []
    for state in states:
        # Extract domain from entity_id (e.g., "light.living_room" -> "light")
        entity_domain = state["entity_id"].split(".")[0] if "." in state["entity_id"] else "unknown"

        # Filter by domain if specified
        if domain and entity_domain != domain:
            continue

        # Extract friendly name from attributes
        friendly_name = state.get("attributes", {}).get("friendly_name")

        entities.append(
            EntityState(
                entity_id=state["entity_id"],
                state=state["state"],
                last_changed=state["last_changed"],
                last_updated=state["last_updated"],
                friendly_name=friendly_name,
                domain=entity_domain,
                attributes=state.get("attributes", {}),
            )
        )

    return entities
