import socket
from urllib.parse import urlparse

import httpx
from typing import Optional


def resolve_url_to_ip(url: str) -> str:
    """
    Resolve a URL's hostname to IP address for Docker compatibility.

    In Docker, anyio/httpx can't resolve .local mDNS hostnames properly,
    but socket.gethostbyname() works. This function converts URLs like
    http://homeassistant.local:8123 to http://10.0.0.151:8123
    """
    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        return url

    try:
        ip = socket.gethostbyname(hostname)
        # Reconstruct URL with IP instead of hostname
        if parsed.port:
            netloc = f"{ip}:{parsed.port}"
        else:
            netloc = ip
        return f"{parsed.scheme}://{netloc}{parsed.path}"
    except socket.gaierror:
        # Can't resolve, return original URL
        return url


class HomeAssistantClient:
    """Client for interacting with Home Assistant REST API."""

    def __init__(self, url: str, access_token: str):
        self.url = url.rstrip("/")
        # Resolve hostname to IP for Docker compatibility
        self.resolved_url = resolve_url_to_ip(self.url)
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def test_connection(self) -> tuple[bool, Optional[str]]:
        """
        Test the connection to Home Assistant.

        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.resolved_url}/api/", headers=self.headers)
                if response.status_code == 200:
                    return True, None
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        except httpx.TimeoutException:
            return False, "Connection timeout"
        except httpx.ConnectError:
            return False, "Connection refused - unable to reach Home Assistant"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    async def get_config(self) -> Optional[dict]:
        """
        Fetch Home Assistant configuration and version info.

        Returns:
            Config dict with version info or None on failure
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.resolved_url}/api/config", headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def get_status(self) -> Optional[dict]:
        """
        Get basic API status.

        Returns:
            Status dict or None on failure
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.resolved_url}/api/", headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None

    async def get_states(self) -> Optional[list[dict]]:
        """
        Fetch all entity states from Home Assistant.

        Returns:
            List of entity state dicts or None on failure
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.resolved_url}/api/states", headers=self.headers)
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None


async def test_ha_connection(url: str, access_token: str) -> tuple[bool, Optional[str], Optional[str]]:
    """
    Test connection to Home Assistant and retrieve version.

    Args:
        url: Home Assistant URL
        access_token: Long-lived access token

    Returns:
        Tuple of (success: bool, error_message: Optional[str], version: Optional[str])
    """
    client = HomeAssistantClient(url, access_token)
    success, error = await client.test_connection()

    if not success:
        return False, error, None

    config = await client.get_config()
    version = config.get("version") if config else None

    return True, None, version
