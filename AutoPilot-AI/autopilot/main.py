from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure package root is in sys.path
package_root = Path(__file__).resolve().parent.parent
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

from autopilot.core.models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AutomationStatus,
    AgentRequest,
)
from autopilot.core.approval_assistant import ApprovalAssistant
from autopilot.gui.pyside_app import run_pyside_gui, PYSIDE_AVAILABLE
from autopilot.gui.cli_runner import run_cli_dashboard


def main():
    parser = argparse.ArgumentParser(
        prog="autopilot-ai",
        description="AutoPilot AI: Universal Coding Agent Automation Assistant"
    )
    parser.add_argument("--cli", action="store_true", help="Launch interactive CLI dashboard mode")
    parser.add_argument("--gui", action="store_true", help="Launch desktop PySide6 graphical interface")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry-run simulation mode")
    parser.add_argument("--profile", type=str, choices=["manual", "balanced", "custom"], help="Set active permission profile")
    parser.add_argument("--status", action="store_true", help="Show status and detected agents and exit")
    parser.add_argument("--test-sim", type=str, choices=["safe_test", "workspace_edit", "dangerous_rm"], help="Run a test simulation and exit")

    args = parser.parse_args()

    assistant = ApprovalAssistant()

    if args.dry_run:
        assistant.toggle_dry_run(True)

    if args.profile:
        assistant.switch_profile(args.profile.capitalize())

    # Handle quick flags
    if args.status:
        print("=== AutoPilot AI Agent Diagnostics ===")
        print(f"Status: {assistant.status.value}")
        print(f"Profile: {assistant.config_manager.get_active_profile().name}")
        print(f"Dry-Run: {assistant.is_dry_run()}\n")
        for info in assistant.adapter_registry.get_all_info():
            status_str = "Running" if info.running else ("Installed" if info.installed else "Not Detected")
            print(f"- {info.display_name} ({info.agent_id}): {status_str} [Type: {info.integration_level.value}]")
            if info.limitations:
                print(f"  Note: {'; '.join(info.limitations)}")
        return

    if args.test_sim:
        if args.test_sim == "safe_test":
            req = AgentRequest(
                agent_id="claude_code",
                category=ActionCategory.TEST_RUN,
                command="npm test",
                action_description="Execute test suite",
            )
        elif args.test_sim == "workspace_edit":
            req = AgentRequest(
                agent_id="cursor",
                category=ActionCategory.FILE_EDIT,
                file_path="src/index.ts",
                workspace_path=".",
                action_description="Edit index file",
            )
        else:
            req = AgentRequest(
                agent_id="cursor",
                category=ActionCategory.FILE_DELETE,
                command="rm -rf /",
                action_description="Recursive file delete",
            )
        event = assistant.process_request(req)
        print(json.dumps(event.to_dict(), indent=2))
        return

    # Default launch logic:
    if args.cli:
        run_cli_dashboard(assistant)
    elif args.gui:
        if PYSIDE_AVAILABLE:
            run_pyside_gui(assistant)
        else:
            print("[Warning] PySide6 not installed. Falling back to CLI mode.")
            run_cli_dashboard(assistant)
    else:
        # If GUI is available and environment has DISPLAY/Windows, run GUI; else CLI
        if PYSIDE_AVAILABLE:
            try:
                run_pyside_gui(assistant)
            except Exception as e:
                print(f"[AutoPilot AI] GUI initialization failed ({e}), starting CLI dashboard...")
                run_cli_dashboard(assistant)
        else:
            run_cli_dashboard(assistant)


if __name__ == "__main__":
    main()
