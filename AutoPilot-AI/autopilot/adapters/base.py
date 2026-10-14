from __future__ import annotations

import abc
from typing import List, Optional, Tuple, Dict, Any
from ..core.models import (
    AgentInfo,
    AgentCapability,
    AgentRequest,
    IntegrationLevel,
)


class BaseAgentAdapter(abc.ABC):
    """
    Abstract Base Class for coding agent adapters.
    Every adapter must explicitly declare its integration level, supported capabilities,
    and technical limitations.
    """

    def __init__(self, agent_id: str, display_name: str, integration_level: IntegrationLevel):
        self.agent_id = agent_id
        self.display_name = display_name
        self.integration_level = integration_level
        self._enabled: bool = True

    @property
    @abc.abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        """List of explicit agent capabilities supported by this adapter."""
        pass

    @property
    @abc.abstractmethod
    def limitations(self) -> List[str]:
        """Known technical limitations and boundaries for this integration."""
        pass

    @abc.abstractmethod
    def detect_installation(self) -> Tuple[bool, str]:
        """
        Check if the target coding agent is installed on this machine.
        Returns (is_installed, version_or_detail_string).
        """
        pass

    @abc.abstractmethod
    def detect_running(self) -> bool:
        """Check if the target coding agent process is currently active."""
        pass

    @abc.abstractmethod
    def intercept_pending_request(self) -> Optional[AgentRequest]:
        """
        Check if the agent is currently requesting permission or approval.
        Returns parsed AgentRequest or None.
        """
        pass

    @abc.abstractmethod
    def execute_approval(self, request: AgentRequest) -> bool:
        """
        Dispatch approval to the agent using the safest supported mechanism.
        Returns True if successfully confirmed.
        """
        pass

    @abc.abstractmethod
    def execute_rejection(self, request: AgentRequest) -> bool:
        """
        Dispatch rejection or cancellation to the agent.
        Returns True if successfully rejected.
        """
        pass

    def get_info(self) -> AgentInfo:
        """Aggregate current status, capabilities, and health information."""
        installed, version = self.detect_installation()
        running = self.detect_running() if installed else False

        # Determine connection health
        if not installed:
            health = "not_installed"
        elif not running:
            health = "idle"
        else:
            health = "healthy"

        return AgentInfo(
            agent_id=self.agent_id,
            display_name=self.display_name,
            integration_level=self.integration_level,
            version=version,
            installed=installed,
            running=running,
            capabilities=self.capabilities,
            limitations=self.limitations,
            connection_health=health,
        )

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
