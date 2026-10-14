from __future__ import annotations

import enum
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any


class ActionCategory(str, enum.Enum):
    FILE_CREATE = "file_create"
    FILE_EDIT = "file_edit"
    TEST_RUN = "test_run"
    BUILD_RUN = "build_run"
    PACKAGE_INSTALL = "package_install"
    NETWORK_ACCESS = "network_access"
    FILE_DELETE = "file_delete"
    ADMIN_PRIVILEGES = "admin_privileges"
    SENSITIVE_OP = "sensitive_op"
    UNKNOWN = "unknown"


class RiskLevel(str, enum.Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionOutcome(str, enum.Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    BLOCKED_EMERGENCY = "blocked_emergency"
    DRY_RUN_APPROVED = "dry_run_approved"
    DRY_RUN_DENIED = "dry_run_denied"


class IntegrationLevel(str, enum.Enum):
    NATIVE_API = "native_api"              # Direct API / IPC protocol supported by agent
    CONFIG_OVERRIDE = "config_override"    # Agent configuration files/settings injection
    CLI_WRAPPER = "cli_wrapper"            # CLI invocation / stdin piping
    WINDOW_ACCESSIBILITY = "window_ui"     # Accessibility / UI automation fallback
    UNSUPPORTED = "unsupported"            # Detected but cannot safely automate


class AutomationStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class AgentCapability:
    name: str
    supported: bool
    description: str


@dataclass
class AgentInfo:
    agent_id: str
    display_name: str
    integration_level: IntegrationLevel
    version: str = "Unknown"
    installed: bool = False
    running: bool = False
    process_name: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    connection_health: str = "healthy"  # healthy, degraded, unavailable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "integration_level": self.integration_level.value,
            "version": self.version,
            "installed": self.installed,
            "running": self.running,
            "process_name": self.process_name,
            "capabilities": [asdict(c) for c in self.capabilities],
            "limitations": self.limitations,
            "connection_health": self.connection_health,
        }


@dataclass
class AgentRequest:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_id: str = "generic"
    agent_name: str = "Generic Agent"
    category: ActionCategory = ActionCategory.UNKNOWN
    action_description: str = ""
    command: Optional[str] = None
    file_path: Optional[str] = None
    workspace_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "category": self.category.value,
            "action_description": self.action_description,
            "command": self.command,
            "file_path": self.file_path,
            "workspace_path": self.workspace_path,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class EvaluationResult:
    outcome: DecisionOutcome
    reason: str
    risk_level: RiskLevel
    matched_rule: Optional[str] = None
    auto_approved: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "reason": self.reason,
            "risk_level": self.risk_level.value,
            "matched_rule": self.matched_rule,
            "auto_approved": self.auto_approved,
            "timestamp": self.timestamp,
        }


@dataclass
class PermissionProfile:
    name: str
    description: str
    auto_approve_categories: List[str] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=list)
    allowed_path_patterns: List[str] = field(default_factory=list)
    blocked_path_patterns: List[str] = field(default_factory=list)
    require_workspace_containment: bool = True
    allow_network: bool = False
    allow_package_install: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PermissionProfile:
        return cls(
            name=data.get("name", "Unnamed"),
            description=data.get("description", ""),
            auto_approve_categories=data.get("auto_approve_categories", []),
            allowed_commands=data.get("allowed_commands", []),
            blocked_commands=data.get("blocked_commands", []),
            allowed_path_patterns=data.get("allowed_path_patterns", []),
            blocked_path_patterns=data.get("blocked_path_patterns", []),
            require_workspace_containment=data.get("require_workspace_containment", True),
            allow_network=data.get("allow_network", False),
            allow_package_install=data.get("allow_package_install", False),
        )


@dataclass
class ApprovalEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    request: AgentRequest = field(default_factory=AgentRequest)
    evaluation: EvaluationResult = field(
        default_factory=lambda: EvaluationResult(
            outcome=DecisionOutcome.PENDING,
            reason="Uninitialized",
            risk_level=RiskLevel.MEDIUM
        )
    )
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "request": self.request.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "timestamp": self.timestamp,
        }
