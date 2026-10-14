from __future__ import annotations

import sys
import time
from typing import Optional
from ..core.models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AutomationStatus,
    AgentRequest,
    ApprovalEvent,
)
from ..core.approval_assistant import ApprovalAssistant


class CLIDashboard:
    """
    Zero-dependency, clean interactive terminal dashboard for AutoPilot AI.
    Runs on headless servers, SSH sessions, or systems without GUI libraries.
    """

    def __init__(self, assistant: Optional[ApprovalAssistant] = None):
        self.assistant = assistant or ApprovalAssistant()

    def print_banner(self):
        print("\033[1;34m" + "=" * 65 + "\033[0m")
        print("\033[1;36m  ⚡ AUTOPILOT AI — Universal Coding Agent Automation Assistant\033[0m")
        print("\033[1;34m" + "=" * 65 + "\033[0m")

    def print_status(self):
        status = self.assistant.status.value.upper()
        prof = self.assistant.config_manager.get_active_profile().name
        dry_run = "ON" if self.assistant.is_dry_run() else "OFF"
        pending = len(self.assistant.get_pending_requests())

        status_color = "\033[1;32m" if status == "ACTIVE" else ("\033[1;31m" if "STOP" in status else "\033[1;33m")
        print(f" Status: {status_color}{status}\033[0m | Profile: \033[1;35m{prof}\033[0m | Dry-Run: \033[1;33m{dry_run}\033[0m | Pending: \033[1;36m{pending}\033[0m")
        print("-" * 65)

    def print_menu(self):
        print("\n\033[1mCommands:\033[0m")
        print(" [1] 📊 View Agents Health & Integrations")
        print(" [2] ⏳ View Pending Approvals Queue")
        print(" [3] 📜 View Recent Audit & Decision Logs")
        print(" [4] ⚖️ Switch Profile (Manual / Balanced / Custom)")
        print(" [5] 🧪 Toggle Dry-Run Mode")
        print(" [6] ⏯️ Start / Pause Automation")
        print(" [7] 🚨 EMERGENCY STOP")
        print(" [8] 🎯 Run Test Simulation (Safe Test / File Edit / Dangerous)")
        print(" [9] ❌ Exit")

    def show_agents(self):
        print("\n\033[1;36m=== Configured Coding Agent Integrations ===\033[0m")
        infos = self.assistant.adapter_registry.get_all_info()
        for info in infos:
            icon = "🟢" if info.running else ("🟡" if info.installed else "⚪")
            print(f" {icon} \033[1m{info.display_name}\033[0m ({info.agent_id})")
            print(f"    - Type: {info.integration_level.value}")
            print(f"    - Status: {'Running' if info.running else ('Installed' if info.installed else 'Not Detected')}")
            caps = ", ".join(c.name for c in info.capabilities if c.supported)
            print(f"    - Capabilities: {caps or 'None'}")
            if info.limitations:
                print(f"    - Limitations: {'; '.join(info.limitations)}")
            print()

    def show_pending(self):
        pending = self.assistant.get_pending_requests()
        print(f"\n\033[1;33m=== Pending Decisions ({len(pending)}) ===\033[0m")
        if not pending:
            print(" No actions currently pending user approval.")
            return

        for idx, req in enumerate(pending, 1):
            print(f" [{idx}] ID: {req.id} | Agent: {req.agent_name} | Category: {req.category.value}")
            if req.command:
                print(f"     Command: {req.command}")
            if req.file_path:
                print(f"     File:    {req.file_path}")
            print(f"     Action:  {req.action_description}")

        choice = input("\nEnter ID to [a]pprove or [d]eny (e.g. 'a <id>' or 'd <id>', or Enter to back): ").strip()
        if choice.startswith("a "):
            req_id = choice.split(" ")[1]
            if self.assistant.user_approve_pending(req_id):
                print(f"\033[1;32mRequest {req_id} approved!\033[0m")
            else:
                print("Request ID not found.")
        elif choice.startswith("d "):
            req_id = choice.split(" ")[1]
            if self.assistant.user_deny_pending(req_id):
                print(f"\033[1;31mRequest {req_id} denied.\033[0m")
            else:
                print("Request ID not found.")

    def show_logs(self):
        events = self.assistant.event_logger.get_recent_events(20)
        print(f"\n\033[1;35m=== Recent Activity Logs ({len(events)}) ===\033[0m")
        if not events:
            print(" No logs recorded yet.")
            return

        for ev in reversed(events):
            t_str = time.strftime("%H:%M:%S", time.localtime(ev.timestamp))
            outcome = ev.evaluation.outcome.value.upper()
            agent = ev.request.agent_name
            cat = ev.request.category.value
            desc = ev.request.command or ev.request.file_path or ev.request.action_description or "Action"
            print(f" [{t_str}] [{outcome:<10}] [{agent}] ({cat}) {desc[:40]} -> {ev.evaluation.reason}")

    def switch_profile_menu(self):
        print("\nAvailable profiles:")
        print(" 1. Balanced (Default safe auto-approvals for test/build/edit in workspace)")
        print(" 2. Manual (Zero auto-approvals, 100% user confirmation)")
        print(" 3. Custom (User-defined whitelist regexes)")
        ch = input("Choose (1-3): ").strip()
        if ch == "1":
            self.assistant.switch_profile("Balanced")
            print("Switched to Balanced profile.")
        elif ch == "2":
            self.assistant.switch_profile("Manual")
            print("Switched to Manual profile.")
        elif ch == "3":
            self.assistant.switch_profile("Custom")
            print("Switched to Custom profile.")

    def run_simulation(self):
        print("\nSimulation Choices:")
        print(" 1. Safe Test Execution: 'npm test'")
        print(" 2. Workspace File Edit: 'src/main.ts'")
        print(" 3. Critical Dangerous Command: 'rm -rf /'")
        print(" 4. Sensitive File Access: '.env'")
        ch = input("Choose simulation (1-4): ").strip()
        if ch == "1":
            req = AgentRequest(
                agent_id="claude_code",
                category=ActionCategory.TEST_RUN,
                command="npm test",
                action_description="Execute test suite",
            )
        elif ch == "2":
            req = AgentRequest(
                agent_id="cursor",
                category=ActionCategory.FILE_EDIT,
                file_path="src/main.ts",
                workspace_path=".",
                action_description="Modify TypeScript source",
            )
        elif ch == "3":
            req = AgentRequest(
                agent_id="cursor",
                category=ActionCategory.FILE_DELETE,
                command="rm -rf /",
                action_description="Recursively purge filesystem",
            )
        elif ch == "4":
            req = AgentRequest(
                agent_id="vscode_copilot",
                category=ActionCategory.FILE_EDIT,
                file_path=".env",
                workspace_path=".",
                action_description="Read environment secrets",
            )
        else:
            print("Invalid choice.")
            return

        print("\nEvaluating simulated request...")
        ev = self.assistant.process_request(req)
        print(f"\033[1mOutcome:\033[0m {ev.evaluation.outcome.value.upper()}")
        print(f"\033[1mRisk:\033[0m    {ev.evaluation.risk_level.value.upper()}")
        print(f"\033[1mReason:\033[0m  {ev.evaluation.reason}")
        print(f"\033[1mRule:\033[0m    {ev.evaluation.matched_rule}")

    def loop(self):
        while True:
            self.print_banner()
            self.print_status()
            self.print_menu()
            try:
                choice = input("\nSelect an option (1-9): ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if choice == "1":
                self.show_agents()
            elif choice == "2":
                self.show_pending()
            elif choice == "3":
                self.show_logs()
            elif choice == "4":
                self.switch_profile_menu()
            elif choice == "5":
                new_state = not self.assistant.is_dry_run()
                self.assistant.toggle_dry_run(new_state)
                print(f"Dry-run mode is now {'ENABLED' if new_state else 'DISABLED'}.")
            elif choice == "6":
                if self.assistant.status == AutomationStatus.ACTIVE:
                    self.assistant.pause()
                    print("Automation PAUSED.")
                else:
                    self.assistant.start()
                    print("Automation STARTED.")
            elif choice == "7":
                self.assistant.emergency_stop()
                print("\033[1;31m🚨 EMERGENCY STOP ENGAGED! ALL AUTOMATION SUSPENDED.\033[0m")
            elif choice == "8":
                self.run_simulation()
            elif choice == "9":
                print("Exiting AutoPilot AI.")
                break
            else:
                print("Unknown command.")

            input("\nPress Enter to continue...")


def run_cli_dashboard(assistant: Optional[ApprovalAssistant] = None):
    dashboard = CLIDashboard(assistant)
    dashboard.loop()
