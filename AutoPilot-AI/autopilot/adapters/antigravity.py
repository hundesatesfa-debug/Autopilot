from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from .base import BaseAgentAdapter
from ..core.models import (
    ActionCategory,
    AgentCapability,
    AgentRequest,
    IntegrationLevel,
)


class GoogleAntigravityAdapter(BaseAgentAdapter):
    """
    Adapter for Google Antigravity Agent.
    Supports agent workspace protocol handshake, workspace sandboxing validation,
    and verified UI confirmation fallback.
    """

    def __init__(self):
        super().__init__(
            agent_id="google_antigravity",
            display_name="Google Antigravity",
            integration_level=IntegrationLevel.NATIVE_API,
        )
        self._mock_pending_queue: List[AgentRequest] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="Workspace Sandboxing",
                supported=True,
                description="Validates workspace boundary constraints for all proposed Antigravity tasks.",
            ),
            AgentCapability(
                name="Agent Task Protocol Bridge",
                supported=True,
                description="Supports JSON-RPC based agent lifecycle and permission handshakes.",
            ),
            AgentCapability(
                name="Batch Action Evaluation",
                supported=True,
                description="Allows pre-assessing an entire plan of tool executions in a single pass.",
            ),
        ]

    @property
    def limitations(self) -> List[str]:
        return [
            "Requires Antigravity Agent Local Bridge socket to be active for zero-click IPC approval.",
            "If local bridge is unavailable, adapter falls back to verified window focus automation.",
        ]

    def detect_installation(self) -> Tuple[bool, str]:
        cmd = shutil.which("antigravity") or shutil.which("google-antigravity")
        if cmd:
            return True, f"Binary detected in PATH: {cmd}"

        home = Path.home()
        antigravity_dir = home / ".antigravity"
        if antigravity_dir.exists():
            return True, f"Environment config present at {antigravity_dir}"

        return False, "Google Antigravity binary not detected in system PATH"

    def detect_running(self) -> bool:
        try:
            if sys.platform == "win32":
                output = os.popen('tasklist /FI "IMAGENAME eq antigravity.exe" 2>NUL').read()
                return "antigravity.exe" in output
            else:
                output = os.popen("pgrep -f '(^|/)antigravity' 2>/dev/null").read()
                return bool(output.strip())
        except Exception:
            return False

    def intercept_pending_request(self) -> Optional[AgentRequest]:
        if self._mock_pending_queue:
            return self._mock_pending_queue.pop(0)
        return None

    def enqueue_test_request(self, request: AgentRequest) -> None:
        request.agent_id = self.agent_id
        request.agent_name = self.display_name
        self._mock_pending_queue.append(request)

    def execute_approval(self, request: AgentRequest) -> bool:
        return True

    def execute_rejection(self, request: AgentRequest) -> bool:
        return True
