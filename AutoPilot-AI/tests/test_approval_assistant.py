from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from autopilot.core.models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AutomationStatus,
    AgentRequest,
)
from autopilot.core.config_manager import ConfigManager
from autopilot.core.event_logger import EventLogger
from autopilot.core.approval_assistant import ApprovalAssistant


class TestApprovalAssistant(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.cfg_dir = Path(self.tmp_dir.name) / "config"
        self.log_dir = Path(self.tmp_dir.name) / "logs"

        self.config_mgr = ConfigManager(config_dir=str(self.cfg_dir))
        self.logger = EventLogger(log_dir=str(self.log_dir))
        self.assistant = ApprovalAssistant(
            config_manager=self.config_mgr,
            event_logger=self.logger,
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_safe_request_auto_approved(self):
        req = AgentRequest(
            agent_id="claude_code",
            category=ActionCategory.TEST_RUN,
            command="npm test",
            action_description="Run tests",
            workspace_path=str(Path(".").resolve()),
        )
        event = self.assistant.process_request(req)
        self.assertEqual(event.evaluation.outcome, DecisionOutcome.APPROVED)
        self.assertTrue(event.evaluation.auto_approved)
        # Verify event logged in audit trail
        logs = self.logger.get_recent_events()
        self.assertEqual(len(logs), 1)

    def test_emergency_stop_halts_automation(self):
        self.assistant.emergency_stop()
        self.assertEqual(self.assistant.status, AutomationStatus.EMERGENCY_STOP)

        req = AgentRequest(
            agent_id="claude_code",
            category=ActionCategory.TEST_RUN,
            command="npm test",
        )
        event = self.assistant.process_request(req)
        self.assertEqual(event.evaluation.outcome, DecisionOutcome.BLOCKED_EMERGENCY)
        self.assertIn("emergency stop is engaged", event.evaluation.reason.lower())

    def test_reset_emergency_stop(self):
        self.assistant.emergency_stop()
        self.assertEqual(self.assistant.status, AutomationStatus.EMERGENCY_STOP)
        self.assistant.reset_emergency_stop()
        self.assertEqual(self.assistant.status, AutomationStatus.STOPPED)

    def test_dry_run_mode(self):
        self.assistant.toggle_dry_run(True)
        self.assertTrue(self.assistant.is_dry_run())

        req = AgentRequest(
            agent_id="claude_code",
            category=ActionCategory.TEST_RUN,
            command="npm test",
            workspace_path=str(Path(".").resolve()),
        )
        event = self.assistant.process_request(req)
        self.assertEqual(event.evaluation.outcome, DecisionOutcome.DRY_RUN_APPROVED)
        self.assertIn("dry-run simulation", event.evaluation.reason.lower())

    def test_pending_queue_manual_approval(self):
        # Trigger an unwhitelisted command that requires confirmation
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.BUILD_RUN,
            command="custom_unregistered_compiler",
            action_description="Run custom compiler",
        )
        event = self.assistant.process_request(req)
        self.assertEqual(event.evaluation.outcome, DecisionOutcome.PENDING)

        pending = self.assistant.get_pending_requests()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, req.id)

        # Explicitly approve
        approved = self.assistant.user_approve_pending(req.id)
        self.assertTrue(approved)
        self.assertEqual(len(self.assistant.get_pending_requests()), 0)


if __name__ == "__main__":
    unittest.main()
