import asyncio
import socket
from typing import List

import httpx
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
from zeroconf.asyncio import AsyncZeroconf


class DiscoveredController:
    """Represents a discovered Home Assistant instance."""

    def __init__(self, name: str, url: str, addresses: List[str]):
        self.name = name
        self.url = url
        self.addresses = addresses


class HomeAssistantListener(ServiceListener):
    """Listener for Home Assistant mDNS/Zeroconf services."""

    def __init__(self):
        self.discovered = []

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        if info:
            addresses = [
                f"{addr[0]}.{addr[1]}.{addr[2]}.{addr[3]}" for addr in info.parsed_addresses()
            ]
            port = info.port
            url = f"http://{addresses[0]}:{port}" if addresses else None

            if url:
                # Clean up the service name
                display_name = name.replace("._home-assistant._tcp.local.", "")
                self.discovered.append(
                    DiscoveredController(name=display_name, url=url, addresses=addresses)
                )

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass


# Common Home Assistant hostnames/URLs to probe as fallback
COMMON_HA_HOSTS = [
    ("homeassistant.local", 8123),
    ("homeassistant", 8123),
    ("home-assistant.local", 8123),
    ("hass.local", 8123),
]


async def probe_host(hostname: str, port: int) -> dict | None:
    """
    Probe a host to check if it's running Home Assistant.

    Returns discovered controller info if HA is found, None otherwise.
    """
    try:
        # First resolve the hostname to get the IP
        # (we use the IP for the actual connection to avoid anyio DNS issues in Docker)
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

        # Use IP for connection but keep hostname for the returned URL
        url = f"http://{hostname}:{port}"
        ip_url = f"http://{ip}:{port}"

        # Try to reach the HA API using IP (will return 401 if HA is there)
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{ip_url}/api/")
            # HA returns 401 for unauthenticated API requests, or 200 with message
            if response.status_code in (200, 401):
                return {
                    "name": hostname.split(".")[0].replace("-", " ").title(),
                    "url": url,
                    "addresses": [ip],
                }
    except (httpx.ConnectError, httpx.TimeoutException, httpx.ConnectTimeout):
        pass
    return None


async def discover_via_mdns(timeout: int = 5) -> List[dict]:
    """Discover Home Assistant instances via mDNS/Zeroconf."""
    listener = HomeAssistantListener()
    aiozc = AsyncZeroconf()

    try:
        browser = ServiceBrowser(aiozc.zeroconf, "_home-assistant._tcp.local.", listener)
        await asyncio.sleep(timeout)
        browser.cancel()
    finally:
        await aiozc.async_close()

    return [
        {"name": ctrl.name, "url": ctrl.url, "addresses": ctrl.addresses}
        for ctrl in listener.discovered
    ]


async def discover_via_probe() -> List[dict]:
    """Probe common hostnames as fallback when mDNS doesn't work (e.g., in Docker)."""
    tasks = [probe_host(host, port) for host, port in COMMON_HA_HOSTS]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]


async def discover_home_assistant(timeout: int = 5) -> List[dict]:
    """
    Discover Home Assistant instances on the local network.

    Uses mDNS/Zeroconf first, then falls back to probing common hostnames
    (useful when running in Docker where mDNS multicast doesn't work).

    Args:
        timeout: Discovery timeout in seconds for mDNS scan

    Returns:
        List of discovered controllers with name, url, and addresses
    """
    # Try mDNS first
    discovered = await discover_via_mdns(timeout)

    # If mDNS found nothing, try probing common hostnames
    if not discovered:
        discovered = await discover_via_probe()

    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for ctrl in discovered:
        if ctrl["url"] not in seen_urls:
            seen_urls.add(ctrl["url"])
            unique.append(ctrl)

    return unique
