from __future__ import annotations

import os
import sys
import subprocess
from typing import List, Dict, Optional, Tuple


class WindowProcessDetector:
    """
    Cross-platform process and window inspector.
    Safely identifies active coding agent windows without external heavy dependencies.
    """

    KNOWN_AGENT_PROCESSES = {
        "cursor": ["cursor.exe", "cursor"],
        "claude_code": ["claude.exe", "claude"],
        "google_antigravity": ["antigravity.exe", "antigravity", "google-antigravity"],
        "vscode_copilot": ["code.exe", "code"],
    }

    @classmethod
    def get_running_agent_processes(cls) -> Dict[str, bool]:
        """Detect which known coding agents are currently executing."""
        status = {k: False for k in cls.KNOWN_AGENT_PROCESSES}

        try:
            if sys.platform == "win32":
                output = subprocess.check_output("tasklist /FO CSV /NH", shell=True, text=True, stderr=subprocess.DEVNULL)
                lower_output = output.lower()
                for agent_id, proc_names in cls.KNOWN_AGENT_PROCESSES.items():
                    for name in proc_names:
                        if name in lower_output:
                            status[agent_id] = True
                            break
            else:
                output = subprocess.check_output(["ps", "-A", "-o", "comm="], text=True, stderr=subprocess.DEVNULL)
                lower_output = output.lower()
                for agent_id, proc_names in cls.KNOWN_AGENT_PROCESSES.items():
                    for name in proc_names:
                        if name in lower_output:
                            status[agent_id] = True
                            break
        except Exception:
            pass

        return status

    @classmethod
    def get_active_window_title(cls) -> Optional[str]:
        """Get the title of the currently focused window if accessible."""
        try:
            if sys.platform == "win32":
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                length = user32.GetWindowTextLengthW(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value
            elif sys.platform == "darwin":
                cmd = "osascript -e 'tell application \"System Events\" to get name of first application process whose frontmost is true'"
                return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
            else:
                # Linux with xdotool
                cmd = "xdotool getwindowfocus getwindowname"
                return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
