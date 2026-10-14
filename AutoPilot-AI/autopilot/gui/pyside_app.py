from __future__ import annotations

import sys
import time
from typing import Optional

try:
    from PySide6.QtCore import Qt, QTimer, Signal, QObject
    from PySide6.QtGui import QColor, QFont, QIcon, QPalette
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QComboBox,
        QCheckBox,
        QTabWidget,
        QTableWidget,
        QTableWidgetItem,
        QHeaderView,
        QTextEdit,
        QLineEdit,
        QGroupBox,
        QSplitter,
        QDialog,
        QMessageBox,
        QScrollArea,
        QFrame,
    )
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False

from ..core.models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AutomationStatus,
    AgentRequest,
    ApprovalEvent,
    IntegrationLevel,
)
from ..core.approval_assistant import ApprovalAssistant


class OnboardingDialog(QDialog if PYSIDE_AVAILABLE else object):
    """First-run onboarding dialog explaining native vs visual automation and security controls."""

    def __init__(self, parent=None):
        if not PYSIDE_AVAILABLE:
            return
        super().__init__(parent)
        self.setWindowTitle("Welcome to AutoPilot AI — Quick Guide")
        self.setMinimumSize(600, 480)
        self.setStyleSheet("background-color: #121826; color: #FFFFFF;")

        layout = QVBoxLayout(self)

        title = QLabel("🤖 AutoPilot AI — Universal Coding Automation")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #60A5FA; margin-bottom: 8px;")
        layout.addWidget(title)

        intro = QLabel(
            "AutoPilot AI reduces repetitive approval interruptions while keeping you in full control "
            "over dangerous operations."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #94A3B8; font-size: 13px; margin-bottom: 12px;")
        layout.addWidget(intro)

        # Principles box
        box = QGroupBox("Key Concepts & Safety Guarantees")
        box.setStyleSheet("QGroupBox { font-weight: bold; color: #38BDF8; border: 1px solid #334155; border-radius: 8px; padding-top: 14px; margin-top: 8px; }")
        box_layout = QVBoxLayout(box)

        t1 = QLabel("1. 🛡️ Native Integration vs. Visual Automation\n"
                    "   AutoPilot AI prioritizes official settings, workspace protocols, and documented CLI hooks "
                    "before falling back to window detection. We never blindly approve unknown dialogs.")
        t1.setWordWrap(True)
        t1.setStyleSheet("color: #E2E8F0; margin-bottom: 8px;")
        box_layout.addWidget(t1)

        t2 = QLabel("2. ⚖️ Permission Profiles (Manual, Balanced, Custom)\n"
                    "   - Manual: You approve every action.\n"
                    "   - Balanced (Default): Automates routine workspace edits and tests; holds deletions, installs, and network.\n"
                    "   - Custom: Tailor specific regex commands and path whitelist rules.")
        t2.setWordWrap(True)
        t2.setStyleSheet("color: #E2E8F0; margin-bottom: 8px;")
        box_layout.addWidget(t2)

        t3 = QLabel("3. 🧪 Dry-Run Mode\n"
                    "   Test your rules safely. AutoPilot AI evaluates requests and writes audit logs without dispatching actual approvals.")
        t3.setWordWrap(True)
        t3.setStyleSheet("color: #E2E8F0; margin-bottom: 8px;")
        box_layout.addWidget(t3)

        t4 = QLabel("4. 🚨 Immediate Emergency Stop\n"
                    "   One click immediately halts all background automation and locks the approval engine.")
        t4.setWordWrap(True)
        t4.setStyleSheet("color: #F87171; margin-bottom: 4px;")
        box_layout.addWidget(t4)

        layout.addWidget(box)

        btn_ok = QPushButton("Get Started")
        btn_ok.setStyleSheet("background-color: #2563EB; color: white; padding: 10px; font-weight: bold; border-radius: 6px; font-size: 14px;")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)


class AutoPilotMainWindow(QMainWindow if PYSIDE_AVAILABLE else object):
    """Main Desktop Window for AutoPilot AI."""

    def __init__(self, assistant: ApprovalAssistant):
        if not PYSIDE_AVAILABLE:
            raise RuntimeError("PySide6 is required to run the graphical interface.")
        super().__init__()
        self.assistant = assistant
        self.setWindowTitle("AutoPilot AI — Coding Agent Automation")
        self.setMinimumSize(1000, 700)
        self._apply_dark_theme()

        self._init_ui()

        # Connect assistant callbacks
        self.assistant.add_decision_callback(self._on_decision_event)
        self.assistant.add_status_change_callback(self._on_status_change)

        # Refresh timer for agent health & pending queue
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_status)
        self.timer.start(2000)

        # Show onboarding if not shown before
        QTimer.singleShot(400, self._check_first_run)

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #1E293B;
                background: #0F172A;
            }
            QTabBar::tab {
                background: #1E293B;
                color: #94A3B8;
                padding: 10px 18px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #2563EB;
                color: #FFFFFF;
                font-weight: bold;
            }
            QPushButton {
                background-color: #1E293B;
                color: #FFFFFF;
                border: 1px solid #334155;
                padding: 8px 14px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
            QTableWidget {
                background-color: #111827;
                alternate-background-color: #1E293B;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #CBD5E1;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #334155;
            }
        """)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # --- Top Header Bar ---
        header = QHBoxLayout()

        title_col = QVBoxLayout()
        app_title = QLabel("⚡ AutoPilot AI")
        app_title.setFont(QFont("Arial", 16, QFont.Bold))
        app_title.setStyleSheet("color: #60A5FA;")
        sub_title = QLabel("Universal Coding Agent Approval & Automation Engine")
        sub_title.setStyleSheet("color: #94A3B8; font-size: 11px;")
        title_col.addWidget(app_title)
        title_col.addWidget(sub_title)
        header.addLayout(title_col)

        header.addStretch()

        # Profile Selector
        lbl_profile = QLabel("Profile:")
        lbl_profile.setStyleSheet("color: #CBD5E1; font-weight: bold;")
        self.combo_profile = QComboBox()
        self.combo_profile.addItems(["Balanced", "Manual", "Custom"])
        active_p = self.assistant.config_manager.get_active_profile().name
        self.combo_profile.setCurrentText(active_p)
        self.combo_profile.currentTextChanged.connect(self._on_profile_changed)
        header.addWidget(lbl_profile)
        header.addWidget(self.combo_profile)

        # Dry Run Checkbox
        self.chk_dry_run = QCheckBox("Dry-Run Mode")
        self.chk_dry_run.setChecked(self.assistant.is_dry_run())
        self.chk_dry_run.toggled.connect(self._on_dry_run_toggled)
        self.chk_dry_run.setStyleSheet("color: #FBBF24; font-weight: bold; margin-left: 8px;")
        header.addWidget(self.chk_dry_run)

        # Global Switch Button
        self.btn_toggle_auto = QPushButton("Automation: ACTIVE")
        self.btn_toggle_auto.setStyleSheet("background-color: #059669; font-weight: bold; padding: 8px 16px;")
        self.btn_toggle_auto.clicked.connect(self._toggle_automation)
        header.addWidget(self.btn_toggle_auto)

        # Emergency Stop Button
        self.btn_emergency = QPushButton("🚨 EMERGENCY STOP")
        self.btn_emergency.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.btn_emergency.clicked.connect(self._emergency_stop)
        header.addWidget(self.btn_emergency)

        main_layout.addLayout(header)

        # --- Main Tabs ---
        self.tabs = QTabWidget()
        self.tab_dashboard = self._create_dashboard_tab()
        self.tab_pending = self._create_pending_tab()
        self.tab_rules = self._create_rules_tab()
        self.tab_history = self._create_history_tab()
        self.tab_agents = self._create_agents_tab()

        self.tabs.addTab(self.tab_dashboard, "📊 Dashboard")
        self.tabs.addTab(self.tab_pending, "⏳ Pending Approvals (0)")
        self.tabs.addTab(self.tab_rules, "⚙️ Permission Rules")
        self.tabs.addTab(self.tab_history, "📜 Audit & Activity Log")
        self.tabs.addTab(self.tab_agents, "🤖 Integrations & Health")

        main_layout.addWidget(self.tabs)

    def _create_dashboard_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # Metric cards row
        card_row = QHBoxLayout()

        self.card_status = self._make_metric_card("Status", "ACTIVE", "#10B981")
        self.card_pending = self._make_metric_card("Pending Decisions", "0", "#F59E0B")
        self.card_approved = self._make_metric_card("Auto-Approved", "0", "#3B82F6")
        self.card_blocked = self._make_metric_card("Blocked / Denied", "0", "#EF4444")

        card_row.addWidget(self.card_status)
        card_row.addWidget(self.card_pending)
        card_row.addWidget(self.card_approved)
        card_row.addWidget(self.card_blocked)
        layout.addLayout(card_row)

        # Middle section: Quick agent summary & Quick test simulator
        middle_row = QHBoxLayout()

        # Agents quick box
        agents_box = QGroupBox("Detected Coding Agents")
        agents_layout = QVBoxLayout(agents_box)
        self.lbl_agent_summary = QLabel("Inspecting agents...")
        self.lbl_agent_summary.setStyleSheet("color: #E2E8F0; font-size: 13px;")
        agents_layout.addWidget(self.lbl_agent_summary)
        middle_row.addWidget(agents_box)

        # Test simulator box
        sim_box = QGroupBox("Action Simulation Sandbox")
        sim_layout = QVBoxLayout(sim_box)
        sim_desc = QLabel("Simulate an incoming agent request to verify permission rule behavior:")
        sim_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        sim_layout.addWidget(sim_desc)

        btn_sim_test = QPushButton("Simulate Safe Test: 'npm test'")
        btn_sim_test.clicked.connect(lambda: self._simulate_action("claude_code", "test_run", "npm test", None))
        sim_layout.addWidget(btn_sim_test)

        btn_sim_edit = QPushButton("Simulate Workspace File Edit: 'src/index.ts'")
        btn_sim_edit.clicked.connect(lambda: self._simulate_action("cursor", "file_edit", None, "src/index.ts"))
        sim_layout.addWidget(btn_sim_edit)

        btn_sim_danger = QPushButton("Simulate Dangerous Command: 'rm -rf /'")
        btn_sim_danger.setStyleSheet("color: #F87171;")
        btn_sim_danger.clicked.connect(lambda: self._simulate_action("cursor", "file_delete", "rm -rf /", None))
        sim_layout.addWidget(btn_sim_danger)

        middle_row.addWidget(sim_box)
        layout.addLayout(middle_row)

        # Recent stream preview
        layout.addWidget(QLabel("Recent Activity Stream:"))
        self.txt_recent_stream = QTextEdit()
        self.txt_recent_stream.setReadOnly(True)
        self.txt_recent_stream.setStyleSheet("background-color: #090D16; border: 1px solid #1E293B; color: #A7F3D0; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.txt_recent_stream)

        return w

    def _make_metric_card(self, title: str, val: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"background-color: #1E293B; border-radius: 8px; border-left: 4px solid {color}; padding: 10px;")
        l = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: bold;")
        v = QLabel(val)
        v.setFont(QFont("Arial", 18, QFont.Bold))
        v.setStyleSheet(f"color: {color};")
        card.val_label = v
        l.addWidget(t)
        l.addWidget(v)
        return card

    def _create_pending_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Decisions awaiting your explicit review and confirmation:"))
        self.table_pending = QTableWidget(0, 6)
        self.table_pending.setHorizontalHeaderLabels(["ID", "Agent", "Category", "Details", "Risk", "Actions"])
        self.table_pending.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_pending)
        return w

    def _create_rules_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        lbl = QLabel("Active Profile: " + self.assistant.config_manager.get_active_profile().name)
        lbl.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(lbl)

        box_cmds = QGroupBox("Allowed Command Patterns (Regex)")
        l_cmds = QVBoxLayout(box_cmds)
        self.txt_allowed_cmds = QTextEdit()
        self.txt_allowed_cmds.setPlaceholderText("One regex per line...")
        l_cmds.addWidget(self.txt_allowed_cmds)
        layout.addWidget(box_cmds)

        box_blocked = QGroupBox("Blocked Command Patterns (Strict Rejections)")
        l_blocked = QVBoxLayout(box_blocked)
        self.txt_blocked_cmds = QTextEdit()
        self.txt_blocked_cmds.setPlaceholderText("One regex per line...")
        l_blocked.addWidget(self.txt_blocked_cmds)
        layout.addWidget(box_blocked)

        self._populate_rules_fields()

        btn_save_rules = QPushButton("Save Rules to Profile")
        btn_save_rules.setStyleSheet("background-color: #2563EB; font-weight: bold;")
        btn_save_rules.clicked.connect(self._save_rules)
        layout.addWidget(btn_save_rules)

        return w

    def _create_history_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("Full Audit Trail & Decision Logs:"))
        header_row.addStretch()
        btn_clear = QPushButton("Clear History")
        btn_clear.clicked.connect(self._clear_logs)
        header_row.addWidget(btn_clear)
        layout.addLayout(header_row)

        self.table_history = QTableWidget(0, 6)
        self.table_history.setHorizontalHeaderLabels(["Timestamp", "Outcome", "Risk", "Agent", "Category", "Reason"])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_history)

        return w

    def _create_agents_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        layout.addWidget(QLabel("Configured Coding Agent Integrations:"))
        self.table_agents = QTableWidget(0, 5)
        self.table_agents.setHorizontalHeaderLabels(["Agent", "Integration Type", "Status", "Capabilities", "Limitations"])
        self.table_agents.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_agents)
        return w

    def _check_first_run(self):
        # Open onboarding dialog
        d = OnboardingDialog(self)
        d.exec()

    def _refresh_status(self):
        # Update metric cards
        events = self.assistant.event_logger.get_recent_events(100)
        pending = len(self.assistant.get_pending_requests())
        auto_approved = sum(1 for e in events if e.evaluation.outcome in (DecisionOutcome.APPROVED, DecisionOutcome.DRY_RUN_APPROVED))
        blocked = sum(1 for e in events if e.evaluation.outcome in (DecisionOutcome.DENIED, DecisionOutcome.BLOCKED_EMERGENCY, DecisionOutcome.DRY_RUN_DENIED))

        self.card_pending.val_label.setText(str(pending))
        self.card_approved.val_label.setText(str(auto_approved))
        self.card_blocked.val_label.setText(str(blocked))
        self.card_status.val_label.setText(self.assistant.status.value.upper())

        self.tabs.setTabText(1, f"⏳ Pending Approvals ({pending})")

        # Update Agent summary
        infos = self.assistant.adapter_registry.get_all_info()
        summary_lines = []
        for info in infos:
            icon = "🟢" if info.running else ("🟡" if info.installed else "⚪")
            summary_lines.append(f"{icon} {info.display_name}: {info.integration_level.value} ({info.connection_health})")
        self.lbl_agent_summary.setText("\n".join(summary_lines))

        # Update Agent table
        self.table_agents.setRowCount(len(infos))
        for row, info in enumerate(infos):
            self.table_agents.setItem(row, 0, QTableWidgetItem(info.display_name))
            self.table_agents.setItem(row, 1, QTableWidgetItem(info.integration_level.value))
            status_str = "Running" if info.running else ("Installed" if info.installed else "Not Detected")
            self.table_agents.setItem(row, 2, QTableWidgetItem(status_str))
            caps = ", ".join(c.name for c in info.capabilities if c.supported)
            self.table_agents.setItem(row, 3, QTableWidgetItem(caps or "Standard"))
            limits = "; ".join(info.limitations)
            self.table_agents.setItem(row, 4, QTableWidgetItem(limits or "None"))

    def _on_decision_event(self, event: ApprovalEvent):
        timestamp_str = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
        outcome = event.evaluation.outcome.value.upper()
        agent = event.request.agent_name
        desc = event.request.action_description or event.request.command or event.request.file_path or "Action"
        reason = event.evaluation.reason

        line = f"[{timestamp_str}] [{outcome}] [{agent}] {desc} -> {reason}"
        self.txt_recent_stream.append(line)

        # Refresh history table
        self._refresh_history_table()

    def _refresh_history_table(self):
        events = self.assistant.event_logger.get_recent_events(50)
        self.table_history.setRowCount(len(events))
        for row, ev in enumerate(events):
            t_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ev.timestamp))
            self.table_history.setItem(row, 0, QTableWidgetItem(t_str))
            self.table_history.setItem(row, 1, QTableWidgetItem(ev.evaluation.outcome.value.upper()))
            self.table_history.setItem(row, 2, QTableWidgetItem(ev.evaluation.risk_level.value.upper()))
            self.table_history.setItem(row, 3, QTableWidgetItem(ev.request.agent_name))
            self.table_history.setItem(row, 4, QTableWidgetItem(ev.request.category.value))
            self.table_history.setItem(row, 5, QTableWidgetItem(ev.evaluation.reason))

    def _on_status_change(self, status: AutomationStatus):
        if status == AutomationStatus.EMERGENCY_STOP:
            self.btn_toggle_auto.setText("Automation: LOCKED")
            self.btn_toggle_auto.setStyleSheet("background-color: #7F1D1D; color: #FCA5A5;")
        elif status == AutomationStatus.ACTIVE:
            self.btn_toggle_auto.setText("Automation: ACTIVE")
            self.btn_toggle_auto.setStyleSheet("background-color: #059669; color: white;")
        elif status == AutomationStatus.PAUSED:
            self.btn_toggle_auto.setText("Automation: PAUSED")
            self.btn_toggle_auto.setStyleSheet("background-color: #D97706; color: white;")
        else:
            self.btn_toggle_auto.setText("Automation: STOPPED")
            self.btn_toggle_auto.setStyleSheet("background-color: #475569; color: white;")

    def _toggle_automation(self):
        if self.assistant.status == AutomationStatus.EMERGENCY_STOP:
            reply = QMessageBox.question(
                self,
                "Reset Emergency Stop",
                "Emergency Stop is active. Reset engine to STOPPED state?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.assistant.reset_emergency_stop()
        elif self.assistant.status == AutomationStatus.ACTIVE:
            self.assistant.pause()
        else:
            self.assistant.start()

    def _emergency_stop(self):
        self.assistant.emergency_stop()
        QMessageBox.warning(
            self,
            "🚨 EMERGENCY STOP ACTIVATED",
            "AutoPilot AI has immediately halted all automated approvals.\n"
            "Pending actions are suspended. You can review all events in the audit log.",
        )

    def _on_profile_changed(self, name: str):
        self.assistant.switch_profile(name)
        self._populate_rules_fields()

    def _on_dry_run_toggled(self, checked: bool):
        self.assistant.toggle_dry_run(checked)

    def _populate_rules_fields(self):
        prof = self.assistant.config_manager.get_active_profile()
        self.txt_allowed_cmds.setText("\n".join(prof.allowed_commands))
        self.txt_blocked_cmds.setText("\n".join(prof.blocked_commands))

    def _save_rules(self):
        prof = self.assistant.config_manager.get_active_profile()
        prof.allowed_commands = [c.strip() for c in self.txt_allowed_cmds.toPlainText().splitlines() if c.strip()]
        prof.blocked_commands = [c.strip() for c in self.txt_blocked_cmds.toPlainText().splitlines() if c.strip()]
        self.assistant.config_manager.save_profiles()
        self.assistant.permission_engine.set_profile(prof)
        QMessageBox.information(self, "Rules Saved", f"Rules for profile '{prof.name}' updated successfully.")

    def _clear_logs(self):
        self.assistant.event_logger.clear_logs()
        self.txt_recent_stream.clear()
        self._refresh_history_table()

    def _simulate_action(self, agent_id: str, category_str: str, command: Optional[str], file_path: Optional[str]):
        req = AgentRequest(
            agent_id=agent_id,
            category=ActionCategory(category_str),
            action_description=f"Simulated execution: {command or file_path}",
            command=command,
            file_path=file_path,
            workspace_path=".",
        )
        self.assistant.process_request(req)


def run_pyside_gui(assistant: Optional[ApprovalAssistant] = None):
    """Launch PySide6 GUI if available."""
    if not PYSIDE_AVAILABLE:
        print("[AutoPilot AI] PySide6 not installed. Falling back to Interactive CLI Dashboard.")
        from .cli_runner import run_cli_dashboard
        run_cli_dashboard(assistant)
        return

    app = QApplication.instance() or QApplication(sys.argv)
    assistant = assistant or ApprovalAssistant()
    window = AutoPilotMainWindow(assistant)
    window.show()
    sys.exit(app.exec())
