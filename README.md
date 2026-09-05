# CorporateMCP System Inspector

`corporate-mcp-system-inspector` is an observation-only MCP server. Its canonical identity is `corporate.system-inspector`, with capability class `observation` and mutation forbidden.

## Capabilities

The server exposes exactly four tools:

- `system_identity`: OS, platform, architecture, hostname, Python, and server identity/version.
- `system_resources`: CPU count, memory totals/availability, and the relevant local disk.
- `process_summary`: aggregate process count and the current process identity.
- `network_summary`: hostname and bounded local interface/address observations.

Every successful result uses `{ok, server_id, server_version, observation}`. Failures use `{ok, server_id, server_version, error}` with a stable error code and safe message.

## Security boundary

This server does not execute shell, PowerShell, cmd, Python, or arbitrary commands. It does not mutate, delete, install, configure, restart, or kill anything. It does not scan networks, inspect environment variables, read unrelated files, expose command-line arguments, credentials, secrets, or arbitrary file contents.

## CI and local verification

GitHub Actions runs on every push and pull request. It synchronizes the locked uv environment, runs the authoritative unittest suite, compiles/imports the package, verifies the exact MCP tool surface, runs the narrow source security gate, and builds the package.

Run the same essential checks locally:

```powershell
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q src tests scripts
uv run python -c "import corporate_mcp_system_inspector.server"
uv run python scripts/verify_mcp_surface.py
uv run python scripts/verify_security_boundary.py
uv build
```

Run the server locally with `uv run corporate-mcp-system-inspector` (or `uv run python -m corporate_mcp_system_inspector`) when MCP stdio interaction is needed.

The server communicates over MCP stdio when run through the project script.
