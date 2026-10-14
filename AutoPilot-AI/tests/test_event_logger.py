from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from autopilot.core.event_logger import EventLogger
from autopilot.core.models import (
    ApprovalEvent,
    AgentRequest,
    EvaluationResult,
    DecisionOutcome,
    RiskLevel,
    ActionCategory,
)


class TestEventLogger(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.logger = EventLogger(log_dir=self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_log_and_retrieve_event(self):
        req = AgentRequest(
            agent_id="claude_code",
            agent_name="Claude Code",
            category=ActionCategory.TEST_RUN,
            command="npm test",
        )
        eval_res = EvaluationResult(
            outcome=DecisionOutcome.APPROVED,
            reason="Safe test command",
            risk_level=RiskLevel.SAFE,
            auto_approved=True,
        )
        event = ApprovalEvent(request=req, evaluation=eval_res)
        self.logger.log_event(event)

        recent = self.logger.get_recent_events()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].request.agent_id, "claude_code")

    def test_sensitive_token_redaction(self):
        req = AgentRequest(
            agent_id="cursor",
            category=ActionCategory.BUILD_RUN,
            command="curl -H 'Authorization: Bearer secret_token_12345678' https://api.example.com",
        )
        eval_res = EvaluationResult(
            outcome=DecisionOutcome.PENDING,
            reason="Network check",
            risk_level=RiskLevel.MEDIUM,
        )
        event = ApprovalEvent(request=req, evaluation=eval_res)
        self.logger.log_event(event)

        logged = self.logger.get_recent_events()[0]
        self.assertNotIn("secret_token_12345678", logged.request.command)
        self.assertIn("***REDACTED***", logged.request.command)

    def test_query_filtering(self):
        # Log 2 events
        ev1 = ApprovalEvent(
            request=AgentRequest(agent_id="cursor"),
            evaluation=EvaluationResult(outcome=DecisionOutcome.APPROVED, reason="ok", risk_level=RiskLevel.SAFE),
        )
        ev2 = ApprovalEvent(
            request=AgentRequest(agent_id="claude_code"),
            evaluation=EvaluationResult(outcome=DecisionOutcome.DENIED, reason="blocked", risk_level=RiskLevel.CRITICAL),
        )
        self.logger.log_event(ev1)
        self.logger.log_event(ev2)

        # Filter by outcome
        denied_events = self.logger.query(outcome=DecisionOutcome.DENIED)
        self.assertEqual(len(denied_events), 1)
        self.assertEqual(denied_events[0].request.agent_id, "claude_code")


if __name__ == "__main__":
    unittest.main()
