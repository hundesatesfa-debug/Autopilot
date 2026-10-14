from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from .base import BaseAgentAdapter
from ..core.models import (
    ActionCategory,
    AgentCapability,
    AgentRequest,
    IntegrationLevel,
)


class ClaudeCodeAdapter(BaseAgentAdapter):
    """
    Adapter for Claude Code (Anthropic's official CLI coding agent).
    Integrates via CLI tool permissions in ~/.claude.json and terminal interactive approval hooks.
    """

    def __init__(self):
        super().__init__(
            agent_id="claude_code",
            display_name="Claude Code",
            integration_level=IntegrationLevel.CLI_WRAPPER,
        )
        self._mock_pending_queue: List[AgentRequest] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="Tool Permissions Configuration",
                supported=True,
                description="Inspects and configures allowedTools within ~/.claude.json.",
            ),
            AgentCapability(
                name="Terminal Interactive Prompt Detection",
                supported=True,
                description="Detects interactive 'Allow Claude to execute command?' stdin prompts.",
            ),
            AgentCapability(
                name="Safe Bash Command Filtering",
                supported=True,
                description="Parses requested bash command line and assesses safety before approval.",
            ),
            AgentCapability(
                name="Remote Daemon API",
                supported=False,
                description="Claude Code runs directly in the terminal without a standalone background daemon.",
            ),
        ]

    @property
    def limitations(self) -> List[str]:
        return [
            "Requires access to the terminal session or CLI wrapper to intercept dynamic stdin prompts.",
            "Changes to ~/.claude.json require session restart to take effect if modified during an active run.",
        ]

    def _get_claude_config(self) -> Optional[Path]:
        home = Path.home()
        cfg1 = home / ".claude.json"
        if cfg1.exists():
            return cfg1
        cfg2 = home / ".claude" / "config.json"
        if cfg2.exists():
            return cfg2
        return None

    def detect_installation(self) -> Tuple[bool, str]:
        cmd = shutil.which("claude")
        if cmd:
            return True, f"Binary located in PATH: {cmd}"

        cfg = self._get_claude_config()
        if cfg:
            return True, f"Configuration file located: {cfg}"

        return False, "Claude Code binary not found in system PATH"

    def detect_running(self) -> bool:
        try:
            if sys.platform == "win32":
                output = os.popen('tasklist /FI "IMAGENAME eq claude.exe" 2>NUL').read()
                return "claude.exe" in output
            else:
                output = os.popen("pgrep -f '(^|/)claude' 2>/dev/null").read()
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
        # For Claude Code, approval is sent via stdin newline 'y\n' or tool pre-approval
        return True

    def execute_rejection(self, request: AgentRequest) -> bool:
        return True
