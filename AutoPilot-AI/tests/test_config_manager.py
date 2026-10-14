from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from autopilot.core.config_manager import ConfigManager
from autopilot.core.models import PermissionProfile


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.mgr = ConfigManager(config_dir=self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_default_profiles_exist(self):
        self.assertIn("manual", self.mgr.profiles)
        self.assertIn("balanced", self.mgr.profiles)
        self.assertIn("custom", self.mgr.profiles)

    def test_profile_switching(self):
        active = self.mgr.get_active_profile()
        self.assertEqual(active.name.lower(), "balanced")

        success = self.mgr.set_active_profile("manual")
        self.assertTrue(success)
        self.assertEqual(self.mgr.get_active_profile().name.lower(), "manual")

    def test_workspace_management(self):
        self.mgr.add_workspace("./my_project")
        ws = self.mgr.get_workspaces()
        self.assertTrue(any("my_project" in w for w in ws))


if __name__ == "__main__":
    unittest.main()
