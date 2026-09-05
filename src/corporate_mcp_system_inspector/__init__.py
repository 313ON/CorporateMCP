"""CorporateMCP System Inspector package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("corporate-mcp-system-inspector")
except PackageNotFoundError:  # pragma: no cover - only relevant from an unpacked source tree
    __version__ = "unknown"


def main() -> None:
    """Run the MCP server over stdio."""
    from .server import run

    run()
