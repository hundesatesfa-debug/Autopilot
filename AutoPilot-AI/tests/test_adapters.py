from __future__ import annotations

import unittest
from autopilot.adapters.registry import AdapterRegistry
from autopilot.adapters.cursor import CursorAdapter
from autopilot.adapters.claude_code import ClaudeCodeAdapter
from autopilot.adapters.antigravity import GoogleAntigravityAdapter
from autopilot.adapters.vscode_copilot import VSCodeCopilotAdapter
from autopilot.core.models import IntegrationLevel, AgentRequest, ActionCategory


class TestAdapters(unittest.TestCase):

    def setUp(self):
        self.registry = AdapterRegistry()

    def test_builtin_adapters_registered(self):
        adapters = self.registry.get_all_adapters()
        agent_ids = [a.agent_id for a in adapters]
        self.assertIn("cursor", agent_ids)
        self.assertIn("claude_code", agent_ids)
        self.assertIn("google_antigravity", agent_ids)
        self.assertIn("vscode_copilot", agent_ids)

    def test_cursor_adapter_capabilities_and_limitations(self):
        cursor = self.registry.get_adapter("cursor")
        self.assertIsNotNone(cursor)
        self.assertEqual(cursor.display_name, "Cursor")
        self.assertTrue(len(cursor.capabilities) > 0)
        self.assertTrue(len(cursor.limitations) > 0)
        # Verify no false claim of unsupported daemon
        for cap in cursor.capabilities:
            if cap.name == "Native Daemon Protocol":
                self.assertFalse(cap.supported)

    def test_claude_code_adapter_capabilities(self):
        claude = self.registry.get_adapter("claude_code")
        self.assertIsNotNone(claude)
        self.assertEqual(claude.integration_level, IntegrationLevel.CLI_WRAPPER)
        cap_names = [c.name for c in claude.capabilities]
        self.assertIn("Tool Permissions Configuration", cap_names)

    def test_antigravity_adapter(self):
        antigravity = self.registry.get_adapter("google_antigravity")
        self.assertIsNotNone(antigravity)
        self.assertEqual(antigravity.agent_id, "google_antigravity")
        self.assertTrue(len(antigravity.limitations) > 0)

    def test_adapter_info_aggregation(self):
        infos = self.registry.get_all_info()
        self.assertEqual(len(infos), 4)
        for info in infos:
            self.assertIn(info.connection_health, ["healthy", "idle", "not_installed"])


if __name__ == "__main__":
    unittest.main()
