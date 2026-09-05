"""Verify the exact MCP tool registration contract."""

import asyncio

from corporate_mcp_system_inspector.server import mcp

EXPECTED_TOOLS = {
    "system_identity",
    "system_resources",
    "process_summary",
    "network_summary",
}


def main() -> None:
    actual_tools = {tool.name for tool in asyncio.run(mcp.list_tools())}
    if actual_tools != EXPECTED_TOOLS:
        missing = sorted(EXPECTED_TOOLS - actual_tools)
        unexpected = sorted(actual_tools - EXPECTED_TOOLS)
        raise SystemExit(f"MCP tool surface mismatch; missing={missing}, unexpected={unexpected}")
    print(f"MCP tool surface verified: {', '.join(sorted(actual_tools))}")


if __name__ == "__main__":
    main()
