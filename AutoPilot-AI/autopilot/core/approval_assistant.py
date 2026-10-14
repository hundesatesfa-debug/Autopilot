from __future__ import annotations

import time
from collections import deque
from typing import List, Optional, Callable, Dict, Any
from .models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AutomationStatus,
    AgentRequest,
    EvaluationResult,
    ApprovalEvent,
    PermissionProfile,
)
from .permission_engine import PermissionEngine
from .config_manager import ConfigManager
from .event_logger import EventLogger
from ..adapters.registry import AdapterRegistry
from ..adapters.base import BaseAgentAdapter
from ..automation.executor import ApprovalExecutor


class ApprovalAssistant:
    """
    Central orchestration engine for AutoPilot AI.
    Coordinates agent detection, permission evaluation, safe automated approvals,
    dry-run execution, emergency stops, and audit logging.
    """

    def __init__(
        self,
        config_manager: Optional[ConfigManager] = None,
        event_logger: Optional[EventLogger] = None,
        adapter_registry: Optional[AdapterRegistry] = None,
    ):
        self.config_manager = config_manager or ConfigManager()
        self.event_logger = event_logger or EventLogger()
        self.adapter_registry = adapter_registry or AdapterRegistry()
        self.permission_engine = PermissionEngine(self.config_manager.get_active_profile())
        self.executor = ApprovalExecutor(
            rate_limit_per_minute=self.config_manager.config.get("rate_limit_per_minute", 30)
        )

        self._status: AutomationStatus = (
            AutomationStatus.ACTIVE
            if self.config_manager.is_global_automation_enabled()
            else AutomationStatus.STOPPED
        )
        self._pending_queue: deque[AgentRequest] = deque(maxlen=200)
        self._on_decision_callbacks: List[Callable[[ApprovalEvent], None]] = []
        self._on_status_change_callbacks: List[Callable[[AutomationStatus], None]] = []

    @property
    def status(self) -> AutomationStatus:
        return self._status

    def set_status(self, new_status: AutomationStatus) -> None:
        """Update automation status and notify subscribers."""
        self._status = new_status
        is_enabled = new_status == AutomationStatus.ACTIVE
        self.config_manager.set_global_automation_enabled(is_enabled)
        for cb in self._on_status_change_callbacks:
            try:
                cb(new_status)
            except Exception as e:
                print(f"Error in status change callback: {e}")

    def start(self) -> None:
        """Start or resume automation."""
        if self._status != AutomationStatus.EMERGENCY_STOP:
            self.set_status(AutomationStatus.ACTIVE)

    def pause(self) -> None:
        """Pause automated approvals."""
        if self._status == AutomationStatus.ACTIVE:
            self.set_status(AutomationStatus.PAUSED)

    def resume(self) -> None:
        """Resume automated approvals."""
        if self._status == AutomationStatus.PAUSED:
            self.set_status(AutomationStatus.ACTIVE)

    def stop(self) -> None:
        """Stop automation."""
        self.set_status(AutomationStatus.STOPPED)

    def emergency_stop(self) -> None:
        """
        FAIL-SAFE: Immediately halt all automation actions.
        Clears pending automated approvals and engages hard lockout.
        """
        self._status = AutomationStatus.EMERGENCY_STOP
        self.config_manager.set_global_automation_enabled(False)

        # Log emergency stop event
        stop_event = ApprovalEvent(
            request=AgentRequest(
                agent_id="system",
                agent_name="AutoPilot AI",
                category=ActionCategory.SENSITIVE_OP,
                action_description="EMERGENCY STOP TRIGGERED BY USER",
            ),
            evaluation=EvaluationResult(
                outcome=DecisionOutcome.BLOCKED_EMERGENCY,
                reason="Immediate emergency stop engaged. All automated approvals suspended.",
                risk_level=RiskLevel.CRITICAL,
                matched_rule="system:emergency_stop",
                auto_approved=False,
            ),
        )
        self.event_logger.log_event(stop_event)

        for cb in self._on_status_change_callbacks:
            try:
                cb(AutomationStatus.EMERGENCY_STOP)
            except Exception:
                pass

    def reset_emergency_stop(self) -> None:
        """Reset emergency stop state back to stopped (requiring user to manually start)."""
        if self._status == AutomationStatus.EMERGENCY_STOP:
            self.set_status(AutomationStatus.STOPPED)

    def switch_profile(self, profile_name: str) -> bool:
        """Switch active permission profile (manual, balanced, custom)."""
        success = self.config_manager.set_active_profile(profile_name)
        if success:
            new_profile = self.config_manager.get_active_profile()
            self.permission_engine.set_profile(new_profile)
        return success

    def toggle_dry_run(self, enabled: bool) -> None:
        """Toggle dry-run simulation mode."""
        self.config_manager.set_dry_run_mode(enabled)

    def is_dry_run(self) -> bool:
        return self.config_manager.is_dry_run_mode()

    def add_decision_callback(self, cb: Callable[[ApprovalEvent], None]) -> None:
        self._on_decision_callbacks.append(cb)

    def add_status_change_callback(self, cb: Callable[[AutomationStatus], None]) -> None:
        self._on_status_change_callbacks.append(cb)

    def get_pending_requests(self) -> List[AgentRequest]:
        return list(self._pending_queue)

    def process_request(self, request: AgentRequest) -> ApprovalEvent:
        """
        Execute the 6-step Universal Approval Assistant workflow:
        1. Identify the originating application.
        2. Determine the requested action using the best supported integration.
        3. Evaluate the action against the user's configured rules.
        4. Approve only if the action is explicitly allowed and safely identifiable.
        5. Otherwise, leave it pending and notify the user.
        6. Record the decision, reason, and timestamp in the activity log.
        """
        # Step 1: Originating application is identified via request.agent_id
        adapter = self.adapter_registry.get_adapter(request.agent_id)
        if adapter:
            request.agent_name = adapter.display_name

        # Ensure default workspace path is attached if missing
        if not request.workspace_path:
            workspaces = self.config_manager.get_workspaces()
            request.workspace_path = workspaces[0] if workspaces else "."

        # Check Emergency Stop condition
        if self._status == AutomationStatus.EMERGENCY_STOP:
            evaluation = EvaluationResult(
                outcome=DecisionOutcome.BLOCKED_EMERGENCY,
                reason="Emergency stop is engaged. AutoPilot AI is completely locked.",
                risk_level=RiskLevel.CRITICAL,
                matched_rule="system:emergency_stop",
                auto_approved=False,
            )
            event = ApprovalEvent(request=request, evaluation=evaluation)
            self.event_logger.log_event(event)
            self._notify_event(event)
            return event

        # Check if automation is stopped or paused
        if self._status in (AutomationStatus.STOPPED, AutomationStatus.PAUSED):
            evaluation = EvaluationResult(
                outcome=DecisionOutcome.PENDING,
                reason=f"Automation is currently {self._status.value}. Manual decision required.",
                risk_level=self.permission_engine.assess_risk(request)[0],
                matched_rule=f"system:{self._status.value}",
                auto_approved=False,
            )
            self._pending_queue.append(request)
            event = ApprovalEvent(request=request, evaluation=evaluation)
            self.event_logger.log_event(event)
            self._notify_event(event)
            return event

        # Step 3: Evaluate against configured rules
        evaluation = self.permission_engine.evaluate(request)

        # Step 4: Approve only if explicitly allowed & safe
        is_dry_run = self.is_dry_run()

        if evaluation.outcome == DecisionOutcome.APPROVED:
            if is_dry_run:
                evaluation.outcome = DecisionOutcome.DRY_RUN_APPROVED
                evaluation.reason = f"[DRY-RUN SIMULATION] Would approve: {evaluation.reason}"
            else:
                # Dispatch actual approval
                if adapter:
                    executed = self.executor.execute_approval(adapter, request, dry_run=False)
                    if not executed:
                        evaluation.outcome = DecisionOutcome.PENDING
                        evaluation.reason += " (Dispatch held by safety rate limiter or window check)"
        elif evaluation.outcome == DecisionOutcome.DENIED:
            if is_dry_run:
                evaluation.outcome = DecisionOutcome.DRY_RUN_DENIED
                evaluation.reason = f"[DRY-RUN SIMULATION] Would deny: {evaluation.reason}"
            else:
                if adapter:
                    self.executor.execute_rejection(adapter, request, dry_run=False)
        else:
            # Step 5: Leave pending and notify user
            self._pending_queue.append(request)

        # Step 6: Record decision, reason, and timestamp in activity log
        event = ApprovalEvent(request=request, evaluation=evaluation)
        self.event_logger.log_event(event)
        self._notify_event(event)
        return event

    def user_approve_pending(self, request_id: str) -> bool:
        """User explicitly approves a pending request from the dashboard."""
        target_req = None
        for r in list(self._pending_queue):
            if r.id == request_id:
                target_req = r
                self._pending_queue.remove(r)
                break

        if not target_req:
            return False

        adapter = self.adapter_registry.get_adapter(target_req.agent_id)
        if adapter:
            self.executor.execute_approval(adapter, target_req, dry_run=self.is_dry_run())

        event = ApprovalEvent(
            request=target_req,
            evaluation=EvaluationResult(
                outcome=DecisionOutcome.APPROVED,
                reason="Explicitly approved by user via AutoPilot AI dashboard.",
                risk_level=RiskLevel.LOW,
                matched_rule="user_explicit_approval",
                auto_approved=False,
            ),
        )
        self.event_logger.log_event(event)
        self._notify_event(event)
        return True

    def user_deny_pending(self, request_id: str) -> bool:
        """User explicitly denies a pending request from the dashboard."""
        target_req = None
        for r in list(self._pending_queue):
            if r.id == request_id:
                target_req = r
                self._pending_queue.remove(r)
                break

        if not target_req:
            return False

        adapter = self.adapter_registry.get_adapter(target_req.agent_id)
        if adapter:
            self.executor.execute_rejection(adapter, target_req, dry_run=self.is_dry_run())

        event = ApprovalEvent(
            request=target_req,
            evaluation=EvaluationResult(
                outcome=DecisionOutcome.DENIED,
                reason="Denied by user via AutoPilot AI dashboard.",
                risk_level=RiskLevel.LOW,
                matched_rule="user_explicit_denial",
                auto_approved=False,
            ),
        )
        self.event_logger.log_event(event)
        self._notify_event(event)
        return True

    def _notify_event(self, event: ApprovalEvent) -> None:
        for cb in self._on_decision_callbacks:
            try:
                cb(event)
            except Exception as e:
                print(f"Error in decision callback: {e}")
