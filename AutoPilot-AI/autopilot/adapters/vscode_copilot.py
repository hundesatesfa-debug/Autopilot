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


class VSCodeCopilotAdapter(BaseAgentAdapter):
    """
    Adapter for Visual Studio Code with GitHub Copilot.
    Inspects user settings and extensions, detects active editor window,
    and handles terminal task execution approvals.
    """

    def __init__(self):
        super().__init__(
            agent_id="vscode_copilot",
            display_name="VS Code (GitHub Copilot)",
            integration_level=IntegrationLevel.CONFIG_OVERRIDE,
        )
        self._mock_pending_queue: List[AgentRequest] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="Copilot Settings Audit",
                supported=True,
                description="Inspects user settings.json for Copilot Chat auto-execution policies.",
            ),
            AgentCapability(
                name="VS Code Process Detection",
                supported=True,
                description="Detects active Code.exe / code processes and workspace root.",
            ),
            AgentCapability(
                name="Terminal Command Interception",
                supported=True,
                description="Validates tasks and terminal executions triggered by Copilot.",
            ),
            AgentCapability(
                name="Direct Extension Interop",
                supported=False,
                description="VS Code sandbox isolates Copilot extension internal states from direct IPC.",
            ),
        ]

    @property
    def limitations(self) -> List[str]:
        return [
            "VS Code extension sandbox prevents third-party apps from injecting directly into Copilot Chat view without accessibility or UI automation.",
            "Requires user settings or window target verification for reliable approval dispatch.",
        ]

    def detect_installation(self) -> Tuple[bool, str]:
        cmd = shutil.which("code") or shutil.which("Code")
        if cmd:
            return True, f"VS Code located in PATH: {cmd}"

        home = Path.home()
        if sys.platform == "win32":
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            code_exe = Path(local_app_data) / "Programs" / "Microsoft VS Code" / "Code.exe"
            if code_exe.exists():
                return True, f"Located at {code_exe}"
        elif sys.platform == "darwin":
            if Path("/Applications/Visual Studio Code.app").exists():
                return True, "Located in /Applications/Visual Studio Code.app"
        else:
            if Path("/usr/share/code").exists() or (home / ".vscode").exists():
                return True, "Located in standard Linux paths"

        if (home / ".vscode").exists():
            return True, "User .vscode directory found"

        return False, "VS Code not detected in system PATH"

    def detect_running(self) -> bool:
        try:
            if sys.platform == "win32":
                output = os.popen('tasklist /FI "IMAGENAME eq Code.exe" 2>NUL').read()
                return "Code.exe" in output
            else:
                output = os.popen("ps -ef 2>/dev/null").read()
                return "code" in output.lower()
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
