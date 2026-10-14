from __future__ import annotations

from typing import Dict, List, Optional, Type
from .base import BaseAgentAdapter
from .cursor import CursorAdapter
from .claude_code import ClaudeCodeAdapter
from .antigravity import GoogleAntigravityAdapter
from .vscode_copilot import VSCodeCopilotAdapter
from ..core.models import AgentInfo


class AdapterRegistry:
    """
    Plugin-based registry for coding agent adapters.
    Enables modular discovery, health inspection, and dynamic addition of new agents.
    """

    def __init__(self):
        self._adapters: Dict[str, BaseAgentAdapter] = {}
        self.register_builtins()

    def register_builtins(self) -> None:
        """Register default supported coding agent adapters."""
        self.register(CursorAdapter())
        self.register(ClaudeCodeAdapter())
        self.register(GoogleAntigravityAdapter())
        self.register(VSCodeCopilotAdapter())

    def register(self, adapter: BaseAgentAdapter) -> None:
        """Register an adapter instance."""
        self._adapters[adapter.agent_id] = adapter

    def unregister(self, agent_id: str) -> None:
        if agent_id in self._adapters:
            del self._adapters[agent_id]

    def get_adapter(self, agent_id: str) -> Optional[BaseAgentAdapter]:
        return self._adapters.get(agent_id)

    def get_all_adapters(self) -> List[BaseAgentAdapter]:
        return list(self._adapters.values())

    def get_enabled_adapters(self) -> List[BaseAgentAdapter]:
        return [a for a in self._adapters.values() if a.is_enabled()]

    def get_all_info(self) -> List[AgentInfo]:
        """Aggregate health and info for all registered adapters."""
        return [a.get_info() for a in self._adapters.values()]
