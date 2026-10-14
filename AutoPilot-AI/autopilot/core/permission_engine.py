from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional, List, Tuple
from .models import (
    ActionCategory,
    RiskLevel,
    DecisionOutcome,
    AgentRequest,
    EvaluationResult,
    PermissionProfile,
)


class PermissionEngine:
    """
    Evaluates coding agent approval requests against user-configured permission profiles
    and security boundaries. Implements least-privilege checks, path containment,
    and destructive command detection.
    """

    CRITICAL_COMMAND_PATTERNS = [
        re.compile(r"\b(rm|del|erase|rmdir|rd)\s+(-[a-zA-Z]*[rf]|/s|/q)\b", re.IGNORECASE),
        re.compile(r"\b(format|mkfs|dd|diskpart|fdisk)\b", re.IGNORECASE),
        re.compile(r"\b(sudo|su|runas|doas)\b", re.IGNORECASE),
        re.compile(r"\b(chmod\s+777|chmod\s+-R\s+777|chown)\b", re.IGNORECASE),
        re.compile(r"(curl|wget|Invoke-WebRequest|iwr|Invoke-Expression|iex).*[\|;]\s*(sh|bash|powershell|cmd)", re.IGNORECASE),
        re.compile(r"\b(net\s+user|net\s+localgroup|reg\s+add|reg\s+delete|bcdedit)\b", re.IGNORECASE),
        re.compile(r"(\.ssh[/\\]id_|\.aws[/\\]credentials|\.kube[/\\]config|\.env\b)", re.IGNORECASE),
        re.compile(r"(shutdown|reboot|init\s+0|kill\s+-9\s+1)\b", re.IGNORECASE),
    ]

    SENSITIVE_FILE_PATTERNS = [
        re.compile(r"(^|[/\\])\.env($|\..*)", re.IGNORECASE),
        re.compile(r"(^|[/\\])\.git([/\\]|$)", re.IGNORECASE),
        re.compile(r"(^|[/\\])\.ssh([/\\]|$)", re.IGNORECASE),
        re.compile(r"(^|[/\\])(id_rsa|id_ed25519|id_ecdsa)($|\..*)", re.IGNORECASE),
        re.compile(r"(^|[/\\])(credentials|secrets|tokens)\.(json|ya?ml|xml|txt)$", re.IGNORECASE),
        re.compile(r"^/etc/(passwd|shadow|sudoers)", re.IGNORECASE),
        re.compile(r"^[a-zA-Z]:[/\\]Windows[/\\]System32", re.IGNORECASE),
    ]

    SAFE_READONLY_COMMAND_PATTERNS = [
        re.compile(r"^(git\s+(status|diff|log|branch|show|remote))(\s+.*)?$", re.IGNORECASE),
        re.compile(r"^(ls|dir|find|pwd)(\s+.*)?$", re.IGNORECASE),
        re.compile(r"^(echo|cat|head|tail|grep|wc)(\s+.*)?$", re.IGNORECASE),
        re.compile(r"^(node\s+-v|npm\s+-v|python\s+--version|rustc\s+--version|go\s+version)$", re.IGNORECASE),
    ]

    def __init__(self, profile: Optional[PermissionProfile] = None):
        self.profile = profile or self._create_default_balanced_profile()

    @staticmethod
    def _create_default_balanced_profile() -> PermissionProfile:
        return PermissionProfile(
            name="Balanced",
            description="Automate routine low-risk actions while strictly protecting sensitive operations",
            auto_approve_categories=[
                ActionCategory.FILE_CREATE.value,
                ActionCategory.FILE_EDIT.value,
                ActionCategory.TEST_RUN.value,
                ActionCategory.BUILD_RUN.value,
            ],
            allowed_commands=[
                r"^npm (test|run lint|run build|run format|run typecheck).*$",
                r"^pytest( .*)?$",
                r"^python -m unittest( .*)?$",
                r"^cargo (test|check|build|clippy).*$",
                r"^go (test|build|vet).*$",
                r"^git (status|diff|log|branch).*$",
                r"^ruff (check|format).*$",
                r"^black( .*)?$",
                r"^prettier( .*)?$",
            ],
            blocked_commands=[
                r".*(rm|del|erase)\s+(-r|-rf|-f|/s|/q).*",
                r".*(sudo|su|runas|chmod|chown).*",
                r".*(curl|wget|Invoke-WebRequest|iwr).*\|.*(sh|bash|powershell|cmd).*",
                r".*(\bformat\b|\bmkfs\b|\bdd\b).*",
                r".*(\.ssh|id_rsa|\.env|id_ed25519|credentials).*",
                r".*(net user|net localgroup|reg add|reg delete).*",
            ],
            allowed_path_patterns=[
                r"^src/.*$",
                r"^app/.*$",
                r"^lib/.*$",
                r"^tests?/.*$",
                r"^docs/.*$",
                r"^[a-zA-Z0-9_\-\.]+\.(ts|tsx|js|jsx|py|rs|go|kt|java|cpp|c|h|json|md|yaml|yml|css|html|xml|toml)$",
            ],
            blocked_path_patterns=[
                r".*\.env.*",
                r".*\.git/.*",
                r".*id_rsa.*",
                r".*credentials.*",
                r".*passwd.*",
                r"^[A-Za-z]:[\\/](Windows|Program Files).*",
                r"^/(etc|root|var|bin|sbin|usr).*",
            ],
            require_workspace_containment=True,
            allow_network=False,
            allow_package_install=False,
        )

    def set_profile(self, profile: PermissionProfile) -> None:
        self.profile = profile

    def is_path_within_workspace(self, target_path: str, workspace_root: str) -> bool:
        """
        Verify that target_path is strictly contained within workspace_root,
        preventing directory traversal attacks (../) and absolute paths outside the repo.
        """
        if not target_path or not workspace_root:
            return False

        try:
            ws_resolved = Path(workspace_root).resolve()
            
            # If target_path is relative, resolve relative to workspace_root
            target = Path(target_path)
            if not target.is_absolute():
                target_resolved = (ws_resolved / target).resolve()
            else:
                target_resolved = target.resolve()

            # Check if target_resolved is relative to ws_resolved
            try:
                target_resolved.relative_to(ws_resolved)
                return True
            except ValueError:
                return False
        except Exception:
            return False

    def assess_risk(self, request: AgentRequest) -> Tuple[RiskLevel, List[str]]:
        """Assess inherent risk level and identify risk indicators in the request."""
        reasons: List[str] = []

        # 1. Check critical command risk first
        if request.command:
            cmd = request.command.strip()
            for pattern in self.CRITICAL_COMMAND_PATTERNS:
                if pattern.search(cmd):
                    reasons.append(f"Command matches critical risk pattern: '{pattern.pattern}'")
                    if request.category in (ActionCategory.ADMIN_PRIVILEGES, ActionCategory.SENSITIVE_OP):
                        reasons.append(f"Action requires elevated permissions ({request.category.value})")
                    return RiskLevel.CRITICAL, reasons

        # 2. Category-based baseline risk
        if request.category in (ActionCategory.ADMIN_PRIVILEGES, ActionCategory.SENSITIVE_OP):
            reasons.append(f"Action requires elevated permissions or sensitive operation ({request.category.value})")
            return RiskLevel.CRITICAL, reasons

        if request.category == ActionCategory.FILE_DELETE:
            reasons.append("File deletion is a destructive operation")
            return RiskLevel.HIGH, reasons

        if request.command:
            cmd = request.command.strip()
            if re.search(r"(\bnpm\s+install\b|\bpip\s+install\b|\bcargo\s+add\b|\bgo\s+get\b)", cmd, re.IGNORECASE):
                reasons.append("Command installs external dependencies/packages")
                return RiskLevel.MEDIUM, reasons

            if re.search(r"\b(curl|wget|ssh|scp|ftp|nc|netcat)\b", cmd, re.IGNORECASE):
                reasons.append("Command accesses network resources")
                return RiskLevel.MEDIUM, reasons

        # 3. Check file path risk
        if request.file_path:
            fp = request.file_path.strip()
            for pattern in self.SENSITIVE_FILE_PATTERNS:
                if pattern.search(fp):
                    reasons.append(f"File path touches sensitive pattern: '{fp}'")
                    return RiskLevel.HIGH, reasons

            if request.workspace_path:
                if not self.is_path_within_workspace(fp, request.workspace_path):
                    reasons.append(f"Target path '{fp}' is outside workspace '{request.workspace_path}'")
                    return RiskLevel.HIGH, reasons

        # 4. Safe baseline
        if request.category in (ActionCategory.FILE_CREATE, ActionCategory.FILE_EDIT):
            return RiskLevel.LOW, reasons
        if request.category in (ActionCategory.TEST_RUN, ActionCategory.BUILD_RUN):
            return RiskLevel.SAFE, reasons

        return RiskLevel.LOW, reasons

    def evaluate(self, request: AgentRequest) -> EvaluationResult:
        """
        Evaluate an AgentRequest against the active PermissionProfile.
        Returns an EvaluationResult specifying outcome, risk level, and reason.
        """
        risk_level, risk_reasons = self.assess_risk(request)

        # 1. Manual profile check: Never auto-approves anything
        if self.profile.name.lower() == "manual":
            return EvaluationResult(
                outcome=DecisionOutcome.PENDING,
                reason="Manual profile is active. All agent actions require explicit user confirmation.",
                risk_level=risk_level,
                matched_rule="profile:manual",
                auto_approved=False,
            )

        # 2. Hard block critical risks
        if risk_level == RiskLevel.CRITICAL:
            reason_msg = "Blocked for safety: " + "; ".join(risk_reasons)
            return EvaluationResult(
                outcome=DecisionOutcome.DENIED,
                reason=reason_msg,
                risk_level=risk_level,
                matched_rule="security:critical_risk_boundary",
                auto_approved=False,
            )

        # 3. Workspace containment validation
        if self.profile.require_workspace_containment and request.file_path and request.workspace_path:
            if not self.is_path_within_workspace(request.file_path, request.workspace_path):
                return EvaluationResult(
                    outcome=DecisionOutcome.PENDING,
                    reason=f"Path '{request.file_path}' is outside designated workspace. Manual confirmation required.",
                    risk_level=RiskLevel.HIGH,
                    matched_rule="policy:workspace_containment",
                    auto_approved=False,
                )

        # 4. Blocked command check
        if request.command:
            cmd = request.command.strip()
            for blocked_pat in self.profile.blocked_commands:
                if re.search(blocked_pat, cmd, re.IGNORECASE):
                    return EvaluationResult(
                        outcome=DecisionOutcome.DENIED,
                        reason=f"Command matches blocked pattern: '{blocked_pat}'",
                        risk_level=RiskLevel.HIGH,
                        matched_rule=f"blocked_command:{blocked_pat}",
                        auto_approved=False,
                    )

        # 5. Blocked path check
        if request.file_path:
            fp = request.file_path.strip()
            for blocked_path_pat in self.profile.blocked_path_patterns:
                if re.search(blocked_path_pat, fp, re.IGNORECASE):
                    return EvaluationResult(
                        outcome=DecisionOutcome.PENDING,
                        reason=f"Path matches restricted pattern '{blocked_path_pat}'. User confirmation required.",
                        risk_level=RiskLevel.HIGH,
                        matched_rule=f"blocked_path:{blocked_path_pat}",
                        auto_approved=False,
                    )

        # 6. Category check
        cat_str = request.category.value if isinstance(request.category, ActionCategory) else str(request.category)
        if cat_str not in self.profile.auto_approve_categories:
            return EvaluationResult(
                outcome=DecisionOutcome.PENDING,
                reason=f"Action category '{cat_str}' is not configured for auto-approval in profile '{self.profile.name}'.",
                risk_level=risk_level,
                matched_rule=f"category_not_whitelisted:{cat_str}",
                auto_approved=False,
            )

        # 7. Package install / network special restrictions
        if request.category == ActionCategory.PACKAGE_INSTALL and not self.profile.allow_package_install:
            return EvaluationResult(
                outcome=DecisionOutcome.PENDING,
                reason="Package installation requires manual confirmation under active profile.",
                risk_level=RiskLevel.MEDIUM,
                matched_rule="policy:require_package_confirm",
                auto_approved=False,
            )

        if request.category == ActionCategory.NETWORK_ACCESS and not self.profile.allow_network:
            return EvaluationResult(
                outcome=DecisionOutcome.PENDING,
                reason="External network access requires manual confirmation under active profile.",
                risk_level=RiskLevel.MEDIUM,
                matched_rule="policy:require_network_confirm",
                auto_approved=False,
            )

        # 8. Command whitelist verification (if command specified and whitelist configured)
        if request.command and self.profile.allowed_commands:
            cmd = request.command.strip()
            matched_allowed = False
            matched_rule_str = ""
            for allowed_pat in self.profile.allowed_commands:
                if re.match(allowed_pat, cmd, re.IGNORECASE):
                    matched_allowed = True
                    matched_rule_str = allowed_pat
                    break

            if not matched_allowed:
                return EvaluationResult(
                    outcome=DecisionOutcome.PENDING,
                    reason=f"Command '{cmd}' is not in the allowed command whitelist for profile '{self.profile.name}'.",
                    risk_level=RiskLevel.MEDIUM,
                    matched_rule="command_not_whitelisted",
                    auto_approved=False,
                )
        elif request.command:
            matched_rule_str = "category_default"
        else:
            matched_rule_str = f"category:{cat_str}"

        # 9. All safety checks passed!
        return EvaluationResult(
            outcome=DecisionOutcome.APPROVED,
            reason=f"Action safely evaluated and permitted by '{self.profile.name}' profile rules.",
            risk_level=risk_level,
            matched_rule=matched_rule_str,
            auto_approved=True,
        )
