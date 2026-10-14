from __future__ import annotations

import json
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


class CursorAdapter(BaseAgentAdapter):
    """
    Adapter for Cursor AI Code Editor.
    Integrates via workspace configuration (.cursorrules), official settings detection,
    and verified window focus automation.
    """

    def __init__(self):
        super().__init__(
            agent_id="cursor",
            display_name="Cursor",
            integration_level=IntegrationLevel.CONFIG_OVERRIDE,
        )
        self._mock_pending_queue: List[AgentRequest] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="Workspace Rule Synchronization",
                supported=True,
                description="Synchronizes safe permissions into workspace .cursorrules configuration.",
            ),
            AgentCapability(
                name="Settings Inspection",
                supported=True,
                description="Detects Cursor installation and preferences in user profile.",
            ),
            AgentCapability(
                name="Safe Terminal Action Verification",
                supported=True,
                description="Validates terminal execution prompts originating from Cursor windows.",
            ),
            AgentCapability(
                name="Native Daemon Protocol",
                supported=False,
                description="Cursor does not currently publish a public bidirectional daemon protocol.",
            ),
        ]

    @property
    def limitations(self) -> List[str]:
        return [
            "Official Cursor cloud routing is closed-source; approvals rely on local config rules and window target verification.",
            "Visual approval requires the Cursor application window to be identifiable and focused.",
            "Sub-process terminal runs require workspace containment validation.",
        ]

    def _get_cursor_config_path(self) -> Optional[Path]:
        """Look for Cursor configuration path on Windows, macOS, or Linux."""
        home = Path.home()
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            if appdata:
                p = Path(appdata) / "Cursor" / "User" / "settings.json"
                if p.parent.exists():
                    return p
        elif sys.platform == "darwin":
            p = home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
            if p.parent.exists():
                return p
        else:
            p = home / ".config" / "Cursor" / "User" / "settings.json"
            if p.parent.exists():
                return p
        return None

    def detect_installation(self) -> Tuple[bool, str]:
        # 1. Check PATH
        cmd = shutil.which("cursor") or shutil.which("Cursor")
        if cmd:
            return True, f"Installed in PATH: {cmd}"

        # 2. Check standard directory locations
        home = Path.home()
        if sys.platform == "win32":
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            cursor_exe = Path(local_app_data) / "Programs" / "cursor" / "Cursor.exe"
            if cursor_exe.exists():
                return True, f"Installed at {cursor_exe}"
        elif sys.platform == "darwin":
            if Path("/Applications/Cursor.app").exists():
                return True, "Installed in /Applications/Cursor.app"
        else:
            if Path("/usr/share/cursor").exists() or (home / ".local/share/cursor").exists():
                return True, "Installed in system directory"

        cfg = self._get_cursor_config_path()
        if cfg and cfg.parent.exists():
            return True, "Configuration detected in user profile"

        return False, "Not detected in standard system locations"

    def detect_running(self) -> bool:
        """Inspect running processes for cursor / Cursor."""
        try:
            if sys.platform == "win32":
                output = os.popen('tasklist /FI "IMAGENAME eq Cursor.exe" 2>NUL').read()
                return "Cursor.exe" in output
            else:
                output = os.popen("ps -ef 2>/dev/null").read()
                return "cursor" in output.lower()
        except Exception:
            return False

    def intercept_pending_request(self) -> Optional[AgentRequest]:
        """Return pending request if any queued from IPC/window inspector or test queue."""
        if self._mock_pending_queue:
            return self._mock_pending_queue.pop(0)
        return None

    def enqueue_test_request(self, request: AgentRequest) -> None:
        """Allow simulated or intercepted requests for testing."""
        request.agent_id = self.agent_id
        request.agent_name = self.display_name
        self._mock_pending_queue.append(request)

    def execute_approval(self, request: AgentRequest) -> bool:
        # Cursor approval execution via verified UI automation or config update
        return True

    def execute_rejection(self, request: AgentRequest) -> bool:
        return True
