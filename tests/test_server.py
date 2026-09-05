import asyncio
import re
import unittest

from corporate_mcp_system_inspector import __version__
from corporate_mcp_system_inspector.models import SERVER_ID
from corporate_mcp_system_inspector.server import mcp, network_summary, process_summary, system_identity, system_resources


TOOLS = {"system_identity", "system_resources", "process_summary", "network_summary"}


class ServerContractTests(unittest.TestCase):
    def assert_success(self, result: dict) -> dict:
        self.assertEqual(result["ok"], True)
        self.assertEqual(result["server_id"], SERVER_ID)
        self.assertEqual(result["server_version"], __version__)
        self.assertIsInstance(result["observation"], dict)
        return result["observation"]

    def test_identity_and_version(self):
        observation = self.assert_success(system_identity())
        self.assertEqual(observation["server_id"], SERVER_ID)
        self.assertEqual(observation["server_version"], __version__)
        self.assertTrue(re.fullmatch(r"\d+\.\d+\.\d+", __version__))
        for field in ("operating_system", "platform", "architecture", "hostname", "python_version"):
            self.assertIn(field, observation)

    def test_resource_schema(self):
        observation = self.assert_success(system_resources())
        self.assertIsInstance(observation["cpu_logical_processors"], int)
        for field in ("memory_total_bytes", "memory_available_bytes", "memory_percentage"):
            self.assertIn(field, observation)
        self.assertIn("disks", observation)
        self.assertIsInstance(observation["disks"], list)

    def test_process_schema_has_no_command_line(self):
        observation = self.assert_success(process_summary())
        for field in ("process_count", "current_process_id", "current_process_name"):
            self.assertIn(field, observation)
        self.assertNotIn("command_line", observation)
        self.assertNotIn("cmdline", observation)

    def test_network_schema(self):
        observation = self.assert_success(network_summary())
        self.assertIn("hostname", observation)
        self.assertIsInstance(observation["interfaces"], list)
        for interface in observation["interfaces"]:
            self.assertEqual(set(interface), {"name", "operational_state", "addresses"})

    def test_registered_surface_is_exact(self):
        registered = {tool.name for tool in asyncio.run(mcp.list_tools())}
        self.assertEqual(registered, TOOLS)
        self.assertFalse(any("exec" in name or "shell" in name or "command" in name for name in registered))

    def test_structured_failure(self):
        from corporate_mcp_system_inspector.server import _observe

        result = _observe(lambda: (_ for _ in ()).throw(RuntimeError("secret-token")))
        self.assertEqual(result["ok"], False)
        self.assertEqual(result["error"], {"code": "OBSERVATION_FAILED", "message": "The requested observation could not be collected."})
        self.assertNotIn("secret-token", str(result))

    def test_no_environment_or_secret_fields(self):
        result = {name: function() for name, function in (("identity", system_identity), ("resources", system_resources), ("processes", process_summary), ("network", network_summary))}
        serialized = str(result).lower()
        for forbidden in ("environment", "password", "api_key", "access_token", "private_key", "cookie", "connection_string"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
