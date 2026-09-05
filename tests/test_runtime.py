import json
import shutil
import subprocess
import sys
import unittest


EXPECTED_TOOLS = {
    "system_identity",
    "system_resources",
    "process_summary",
    "network_summary",
}


class RuntimeIntegrationTests(unittest.TestCase):
    def _assert_stdio_handshake(self, command):
        requests = "\n".join(
            [
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "protocolVersion": "2025-03-26",
                            "capabilities": {},
                            "clientInfo": {"name": "corporate-mcp-runtime-test", "version": "1.0"},
                        },
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
            ]
        ) + "\n"

        result = subprocess.run(
            command,
            input=requests,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        responses = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        by_id = {response.get("id"): response for response in responses if "id" in response}

        self.assertEqual(by_id[1]["result"]["serverInfo"]["name"], "corporate.system-inspector")
        self.assertEqual(by_id[1]["result"]["capabilities"]["tools"], {"listChanged": False})
        self.assertEqual(
            {tool["name"] for tool in by_id[2]["result"]["tools"]},
            EXPECTED_TOOLS,
        )

    def test_console_entrypoint_serves_mcp_initialize_and_tools_list(self):
        command = shutil.which("corporate-mcp-system-inspector")
        self.assertIsNotNone(command, "packaged console entrypoint is not available")
        self._assert_stdio_handshake([command])

    def test_module_entrypoint_serves_mcp_initialize_and_tools_list(self):
        self._assert_stdio_handshake([sys.executable, "-m", "corporate_mcp_system_inspector"])


if __name__ == "__main__":
    unittest.main()
