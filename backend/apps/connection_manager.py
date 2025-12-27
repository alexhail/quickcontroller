import asyncio
import logging
from datetime import datetime

from apps.ha_client import HomeAssistantClient
from core.encryption import decrypt_token
from db.postgres import get_pool
from db.redis import get_redis

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages background heartbeat monitoring for Home Assistant controllers."""

    def __init__(self, interval: int = 30):
        self.interval = interval
        self.task: asyncio.Task = None
        self.running = False

    async def start(self):
        """Start the background heartbeat task."""
        if self.running:
            return

        self.running = True
        self.task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Connection manager started")

    async def stop(self):
        """Stop the background heartbeat task."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Connection manager stopped")

    async def _heartbeat_loop(self):
        """Main heartbeat loop - checks all controllers periodically."""
        while self.running:
            try:
                await self._check_all_controllers()
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

            await asyncio.sleep(self.interval)

    async def _check_all_controllers(self):
        """Check status of all registered controllers."""
        async with get_pool().acquire() as conn:
            controllers = await conn.fetch(
                """
                SELECT id, url, access_token_encrypted, connection_status
                FROM master_controllers
                """
            )

        for controller in controllers:
            await self._check_controller(controller)

    async def _check_controller(self, controller: dict):
        """Check a single controller and update its status."""
        controller_id = controller["id"]
        url = controller["url"]
        encrypted_token = controller["access_token_encrypted"]
        old_status = controller["connection_status"]

        try:
            # Decrypt token
            access_token = decrypt_token(encrypted_token)

            # Test connection
            client = HomeAssistantClient(url, access_token)
            success, error = await client.test_connection()

            if success:
                # Get version info
                config = await client.get_config()
                version = config.get("version") if config else None

                # Update to online
                async with get_pool().acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE master_controllers
                        SET connection_status = 'online',
                            last_seen = $1,
                            last_error = NULL,
                            ha_version = $2,
                            updated_at = $1
                        WHERE id = $3
                        """,
                        datetime.utcnow(),
                        version,
                        controller_id,
                    )

                new_status = "online"
            else:
                # Update to offline with error
                async with get_pool().acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE master_controllers
                        SET connection_status = 'offline',
                            last_error = $1,
                            updated_at = $2
                        WHERE id = $3
                        """,
                        error,
                        datetime.utcnow(),
                        controller_id,
                    )

                new_status = "offline"

            # Publish status change event if status changed
            if new_status != old_status:
                await self._publish_status_change(controller_id, old_status, new_status)

        except Exception as e:
            logger.error(f"Error checking controller {controller_id}: {e}")

            # Update to error status
            async with get_pool().acquire() as conn:
                await conn.execute(
                    """
                    UPDATE master_controllers
                    SET connection_status = 'error',
                        last_error = $1,
                        updated_at = $2
                    WHERE id = $3
                    """,
                    str(e),
                    datetime.utcnow(),
                    controller_id,
                )

            if old_status != "error":
                await self._publish_status_change(controller_id, old_status, "error")

    async def _publish_status_change(self, controller_id: str, old_status: str, new_status: str):
        """Publish a status change event to Redis."""
        try:
            redis = get_redis()
            message = f"{controller_id}:{old_status}:{new_status}"
            await redis.publish("controller_status_changes", message)
            logger.info(f"Controller {controller_id} status: {old_status} -> {new_status}")
        except Exception as e:
            logger.error(f"Error publishing status change: {e}")


# Global connection manager instance
_connection_manager: ConnectionManager = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager
