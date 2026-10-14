# Adding New Agent Integrations to AutoPilot AI

AutoPilot AI uses a plugin architecture. Developers can add support for new AI coding tools without modifying the core approval engine.

---

## 1. Adapter Contract (`BaseAgentAdapter`)

Every adapter must inherit from `autopilot.adapters.base.BaseAgentAdapter` and implement:

1. `capabilities`: Explicit list of supported features (`AgentCapability`).
2. `limitations`: Documented known technical limitations. Never falsely claim full native integration when only window detection is available.
3. `detect_installation()`: Returns `(bool, str)` indicating whether the agent is installed.
4. `detect_running()`: Returns `bool` indicating whether the agent process is currently active.
5. `intercept_pending_request()`: Returns `Optional[AgentRequest]` if an approval request is pending.
6. `execute_approval(request)`: Executes the approved action via the safest supported mechanism.
7. `execute_rejection(request)`: Executes rejection or cancellation.

---

## 2. Example: Custom Agent Adapter

Create a new file under `autopilot/adapters/my_agent.py`:

```python
from __future__ import annotations
import shutil
from typing import List, Optional, Tuple
from .base import BaseAgentAdapter
from ..core.models import (
    ActionCategory,
    AgentCapability,
    AgentRequest,
    IntegrationLevel,
)

class MyCustomAgentAdapter(BaseAgentAdapter):
    """Integration for MyCustomAgent."""

    def __init__(self):
        super().__init__(
            agent_id="my_custom_agent",
            display_name="My Custom Agent",
            integration_level=IntegrationLevel.CLI_WRAPPER,
        )

    @property
    def capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="Tool Execution Approval",
                supported=True,
                description="Approves safe CLI tool executions via stdin hook.",
            ),
            AgentCapability(
                name="Remote Daemon Protocol",
                supported=False,
                description="MyCustomAgent does not provide a daemon protocol.",
            ),
        ]

    @property
    def limitations(self) -> List[str]:
        return [
            "Requires active terminal session access.",
            "Visual dialog matching is only active when window is foregrounded.",
        ]

    def detect_installation(self) -> Tuple[bool, str]:
        cmd = shutil.which("my-custom-agent")
        if cmd:
            return True, f"Located at {cmd}"
        return False, "Executable not found in PATH"

    def detect_running(self) -> bool:
        # Check process table
        import sys, os
        if sys.platform == "win32":
            out = os.popen('tasklist /FI "IMAGENAME eq my-custom-agent.exe" 2>NUL').read()
            return "my-custom-agent.exe" in out
        else:
            out = os.popen("pgrep -f my-custom-agent 2>/dev/null").read()
            return bool(out.strip())

    def intercept_pending_request(self) -> Optional[AgentRequest]:
        # Intercept IPC or terminal prompt
        return None

    def execute_approval(self, request: AgentRequest) -> bool:
        # Send confirmation (IPC, stdin, or verified keystroke)
        return True

    def execute_rejection(self, request: AgentRequest) -> bool:
        return True
```

---

## 3. Registering the Adapter

In `autopilot/adapters/registry.py`:

```python
from .my_agent import MyCustomAgentAdapter

class AdapterRegistry:
    def register_builtins(self) -> None:
        ...
        self.register(MyCustomAgentAdapter())
```

---

## 4. Writing Unit Tests

Add a test case in `tests/test_adapters.py`:

```python
def test_my_custom_agent_adapter(self):
    adapter = self.registry.get_adapter("my_custom_agent")
    self.assertIsNotNone(adapter)
    self.assertEqual(adapter.display_name, "My Custom Agent")
    self.assertTrue(len(adapter.capabilities) > 0)
    self.assertTrue(len(adapter.limitations) > 0)
```

Run tests:
```bash
python -m unittest discover -s tests -t .
```
