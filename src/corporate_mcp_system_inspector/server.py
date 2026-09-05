"""MCP entry point for the observation-only System Inspector."""

import asyncio

from mcp.server.mcpserver import MCPServer

from . import __version__
from .models import failure, success
from .observations.network import collect_network_summary
from .observations.processes import collect_process_summary
from .observations.resources import collect_resources
from .observations.system import collect_identity

mcp = MCPServer(
    name="corporate.system-inspector",
    version=__version__,
    instructions="Observation-only system information; no mutation or command execution is available.",
)


def _observe(collector):
    try:
        return success(collector())
    except Exception:
        return failure("OBSERVATION_FAILED", "The requested observation could not be collected.")


@mcp.tool()
def system_identity() -> dict:
    """Return operating-system and runtime identity."""
    return _observe(collect_identity)


@mcp.tool()
def system_resources() -> dict:
    """Return CPU, memory, and local disk observations."""
    return _observe(collect_resources)


@mcp.tool()
def process_summary() -> dict:
    """Return aggregate process information without command lines."""
    return _observe(collect_process_summary)


@mcp.tool()
def network_summary() -> dict:
    """Return bounded local interface and address observations."""
    return _observe(collect_network_summary)


def run() -> None:
    """Run the MCP server over stdio."""
    asyncio.run(mcp.run_stdio_async())
