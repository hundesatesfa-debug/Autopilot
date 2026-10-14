from __future__ import annotations

import time
from collections import deque
from typing import Optional
from ..core.models import (
    AgentRequest,
    DecisionOutcome,
    EvaluationResult,
    RiskLevel,
)
from ..adapters.base import BaseAgentAdapter
from .detector import WindowProcessDetector


class ApprovalExecutor:
    """
    Safely dispatches approvals or rejections to target coding agents.
    Enforces rate limits, dry-run simulation mode, window title verification,
    and fail-safe aborts.
    """

    def __init__(self, rate_limit_per_minute: int = 30):
        self.rate_limit_per_minute = rate_limit_per_minute
        self._recent_approvals: deque[float] = deque()

    def check_rate_limit(self) -> bool:
        """Ensure we do not exceed safe automated approval frequency."""
        now = time.time()
        # Remove timestamps older than 60 seconds
        while self._recent_approvals and self._recent_approvals[0] < now - 60.0:
            self._recent_approvals.popleft()

        if len(self._recent_approvals) >= self.rate_limit_per_minute:
            return False
        return True

    def execute_approval(
        self,
        adapter: BaseAgentAdapter,
        request: AgentRequest,
        dry_run: bool = False,
        verify_window: bool = False,
    ) -> bool:
        """
        Execute an approved action.
        If dry_run is True, returns True without sending actual keystrokes or IPC.
        """
        if dry_run:
            return True

        if not self.check_rate_limit():
            print(f"[ApprovalExecutor] Rate limit exceeded ({self.rate_limit_per_minute}/min). Approval held.")
            return False

        if verify_window:
            active_title = WindowProcessDetector.get_active_window_title()
            if active_title and adapter.display_name.lower() not in active_title.lower():
                print(f"[ApprovalExecutor] Target window mismatch (focused: '{active_title}'). Aborting approval.")
                return False

        success = adapter.execute_approval(request)
        if success:
            self._recent_approvals.append(time.time())
        return success

    def execute_rejection(
        self,
        adapter: BaseAgentAdapter,
        request: AgentRequest,
        dry_run: bool = False,
    ) -> bool:
        """Reject an agent request."""
        if dry_run:
            return True
        return adapter.execute_rejection(request)
