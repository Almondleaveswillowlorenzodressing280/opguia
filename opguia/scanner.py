"""OPC UA server discovery — scan common ports for active servers.

Probes localhost (and optionally other hosts) on standard OPC UA ports
using parallel async connections. Returns a list of reachable servers
with their URL, application name, and port.

Uses a TCP pre-check before attempting OPC UA connect, which is more
reliable cross-platform (especially on Windows where asyncua connect
can hang on unreachable ports).
"""

import asyncio
from asyncua import Client

# Standard OPC UA port is 4840. Others are common vendor defaults.
SCAN_PORTS = [4840, 4841, 4842, 4843, 48400, 48401, 48010, 53530]
SCAN_HOSTS = ["localhost"]


async def _tcp_reachable(host: str, port: int, timeout: float = 1.0) -> bool:
    """Quick TCP connect check — returns True if the port is open."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def _probe(host: str, port: int, timeout: float = 2.0) -> dict | None:
    """Try to connect to a single host:port. Returns server info or None."""
    # Fast TCP pre-check — avoids asyncua hanging on unreachable ports (Windows)
    if not await _tcp_reachable(host, port, timeout=min(timeout, 1.0)):
        return None

    url = f"opc.tcp://{host}:{port}"
    try:
        c = Client(url=url, timeout=timeout)
        await asyncio.wait_for(c.connect(), timeout=timeout)
        try:
            endpoints = await c.get_endpoints()
            name = endpoints[0].Server.ApplicationName.Text if endpoints else ""
            return {"url": url, "name": name or "", "port": port}
        finally:
            await c.disconnect()
    except Exception:
        return None


async def scan_servers(
    hosts: list[str] | None = None,
    ports: list[int] | None = None,
) -> list[dict]:
    """Scan hosts/ports for OPC UA servers. Returns list of {url, name, port}."""
    hosts = hosts or SCAN_HOSTS
    ports = ports or SCAN_PORTS
    tasks = [_probe(h, p) for h in hosts for p in ports]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
