from __future__ import annotations

import unittest
from pathlib import Path
from autopilot.core.models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AgentRequest,
    PermissionProfile,
)
from autopilot.core.permission_engine import PermissionEngine


class TestPermissionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PermissionEngine()
        self.workspace = str(Path(".").resolve())

    def test_balanced_profile_approves_safe_test_command(self):
        req = AgentRequest(
            agent_id="claude_code",
            category=ActionCategory.TEST_RUN,
            command="npm test -- --watch=false",
            action_description="Run project tests",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.APPROVED)
        self.assertTrue(res.auto_approved)

    def test_balanced_profile_approves_workspace_file_edit(self):
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.FILE_EDIT,
            file_path="src/utils/helpers.ts",
            workspace_path=self.workspace,
            action_description="Refactor helper function",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.APPROVED)
        self.assertTrue(res.auto_approved)

    def test_balanced_profile_denies_critical_destructive_command(self):
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.FILE_DELETE,
            command="rm -rf /",
            action_description="Purge directory",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.DENIED)
        self.assertFalse(res.auto_approved)
        self.assertEqual(res.risk_level, RiskLevel.CRITICAL)

    def test_balanced_profile_denies_privilege_escalation(self):
        req = AgentRequest(
            agent_id="claude_code",
            category=ActionCategory.ADMIN_PRIVILEGES,
            command="sudo systemctl restart service",
            action_description="Restart system daemon",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.DENIED)
        self.assertIn("elevated permissions", res.reason.lower())

    def test_path_traversal_detection(self):
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.FILE_EDIT,
            file_path="../../etc/passwd",
            workspace_path=self.workspace,
            action_description="Read system password file",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.PENDING)
        self.assertIn("outside designated workspace", res.reason.lower())

    def test_sensitive_file_protection_env_file(self):
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.FILE_EDIT,
            file_path=".env",
            workspace_path=self.workspace,
            action_description="Modify environment secrets",
        )
        res = self.engine.evaluate(req)
        # Sensitive file patterns should be held pending or denied
        self.assertEqual(res.outcome, DecisionOutcome.PENDING)
        self.assertIn("restricted pattern", res.reason.lower())

    def test_manual_profile_holds_everything_pending(self):
        manual_profile = PermissionProfile(
            name="Manual",
            description="Zero automatic approvals",
            auto_approve_categories=[],
            allowed_commands=[],
            blocked_commands=[".*"],
        )
        self.engine.set_profile(manual_profile)

        req = AgentRequest(
            agent_id="claude_code",
            category=ActionCategory.TEST_RUN,
            command="npm test",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.PENDING)
        self.assertFalse(res.auto_approved)
        self.assertIn("manual profile is active", res.reason.lower())

    def test_unwhitelisted_command_held_pending(self):
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.BUILD_RUN,
            command="some_random_unknown_tool --do-stuff",
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.outcome, DecisionOutcome.PENDING)
        self.assertIn("not in the allowed command whitelist", res.reason)


if __name__ == "__main__":
    unittest.main()
