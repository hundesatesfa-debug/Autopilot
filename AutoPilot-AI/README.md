# ⚡ AutoPilot AI — Universal Coding Agent Automation

AutoPilot AI is a universal automation assistant and security supervisor for AI coding agents such as **Cursor**, **Claude Code**, **Google Antigravity**, and **Visual Studio Code with GitHub Copilot**.

Its mission is to eliminate repetitive permission interruptions during agentic workflows while maintaining uncompromising control over destructive, credential-accessing, and privilege-escalating actions.

---

## 🌟 Key Features

- **Universal Agent Discovery & Health Monitoring**: Automatically checks installed agents, process status, integration mode, and technical capabilities for Cursor, Claude Code, Google Antigravity, and VS Code Copilot.
- **Configurable Permission Profiles**:
  - `Manual`: All approval decisions require explicit user confirmation.
  - `Balanced` *(Default)*: Safely auto-approves routine file creations, edits within workspace bounds, tests, builds, and linting. Holds deletions, package installs, network access, and external paths.
  - `Custom`: User-defined regex rules for allowed/blocked commands and path patterns.
- **Strict Security Boundaries**:
  - **Path Containment**: Guarantees file operations remain strictly within configured workspace boundaries, defeating directory traversal (`../`) and unauthorized root/system file touches.
  - **Dangerous Command Interception**: Blocks `rm -rf`, `format`, `dd`, `sudo`, `chown`, `curl | bash`, and secret reads (`.env`, `id_rsa`).
  - **Never Approves Arbitrary Dialogs**: Evaluates the requested action payload, not the presence of generic UI words like "Allow" or "Approve".
- **Immediate Emergency Stop**: A global one-click fail-safe immediately halts all automated approvals and suspends pending operations.
- **Dry-Run Simulation Mode**: Evaluate policies and review audit logs in real-time without dispatching actual keystrokes or IPC calls.
- **Local & Private by Default**: No cloud dependencies, no paid APIs, no external telemetry. All audit logs and configurations remain strictly on your local machine with automatic API key/token redaction.
- **Dual Interface**: Polished desktop GUI powered by PySide6 (Qt) plus a zero-dependency interactive CLI dashboard for headless, terminal, or remote SSH environments.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Optional: `PySide6` for desktop graphical interface

### Installation
Clone or extract the repository, then navigate to the project directory:
```bash
cd AutoPilot-AI
pip install -r requirements.txt
```

### Running on Windows
Double-click `scripts/run_autopilot.bat` or run in PowerShell:
```powershell
.\scripts\run_autopilot.ps1
```

### Running on macOS / Linux
```bash
chmod +x scripts/run_autopilot.sh
./scripts/run_autopilot.sh
```

### Launch Modes & CLI Flags
```bash
# Launch Desktop GUI (PySide6)
python -m autopilot.main --gui

# Launch Interactive Terminal Dashboard
python -m autopilot.main --cli

# Launch in Dry-Run Mode (Simulation only)
python -m autopilot.main --dry-run

# Run with a specific profile (manual, balanced, custom)
python -m autopilot.main --profile balanced

# Inspect detected agents and integration status
python -m autopilot.main --status

# Run a test simulation request
python -m autopilot.main --test-sim safe_test
python -m autopilot.main --test-sim dangerous_rm
```

---

## 🏗️ Architecture & Integrations

AutoPilot AI uses a plugin-based architecture separating interfaces, adapter hooks, evaluation logic, and safety verification:

```
AutoPilot-AI/
├── autopilot/
│   ├── adapters/            # Modular coding agent adapters
│   │   ├── base.py          # Abstract base declaring capabilities & limitations
│   │   ├── cursor.py        # Cursor IDE settings & workspace rules
│   │   ├── claude_code.py   # Claude Code CLI hooks & tool permissions
│   │   ├── antigravity.py   # Google Antigravity protocol bridge
│   │   ├── vscode_copilot.py# VS Code & Copilot Chat task integration
│   │   └── registry.py      # Dynamic adapter registry & discovery
│   ├── core/                # Core evaluation and orchestration
│   │   ├── models.py        # Domain types, Enums, and request models
│   │   ├── permission_engine.py # Path containment & rule evaluation
│   │   ├── approval_assistant.py# 6-step approval coordinator & Emergency Stop
│   │   ├── config_manager.py# Local JSON configuration & profiles
│   │   └── event_logger.py  # Local audit logging & secret redaction
│   ├── automation/          # Low-level execution & detection
│   │   ├── detector.py      # Process and active window inspection
│   │   └── executor.py      # Rate-limited approval dispatch & dry-run logic
│   └── gui/                 # User interfaces
│       ├── pyside_app.py    # PySide6 desktop GUI with dark theme & onboarding
│       └── cli_runner.py    # Zero-dependency interactive CLI dashboard
├── config/                  # Sample configurations and profiles
├── docs/                    # Technical & security documentation
├── scripts/                 # Launch scripts and packaging utilities
├── tests/                   # Comprehensive automated unit tests
└── pyinstaller.spec         # Standalone Windows executable spec
```

### Supported Integrations Matrix

| Agent | Integration Level | Capabilities | Technical Limitations |
| :--- | :--- | :--- | :--- |
| **Cursor** | `config_override` + window verification | Workspace `.cursorrules` sync, settings inspection, safe terminal verification | Closed-source router backend; approvals rely on local configs and active window verification |
| **Claude Code** | `cli_wrapper` + stdin hook | `~/.claude.json` tool permissions, interactive terminal prompt parsing | Requires terminal session access; daemon not standalone |
| **Google Antigravity** | `native_api` / protocol bridge | Workspace boundary sandboxing, JSON-RPC agent lifecycle, batch action evaluation | Local bridge socket required for zero-click IPC; falls back to window focus check |
| **VS Code Copilot** | `config_override` + task hook | Settings inspection, process detection, task verification | Extension sandbox isolates chat UI; requires window focus or user settings policy |

---

## 🔒 Security Principles

1. **Least Privilege**: Only actions explicitly whitelisted in the active profile are automated.
2. **Path Sandboxing**: Target files must strictly resolve inside authorized workspace directories. Path traversal attacks (`../`, `/etc/`, `C:\Windows`) are blocked or held pending.
3. **Destructive Command Blocking**: Commands matching patterns like `rm -rf`, `mkfs`, `sudo`, `dd`, or piping remote web content into shells (`curl | sh`) are automatically blocked.
4. **Secret Protection**: File paths touching `.env`, `.git`, `.ssh`, or private keys require manual confirmation. All activity logs automatically mask API keys and credentials.
5. **Fail-Safe Emergency Stop**: The emergency stop state is sticky and cannot be overridden by agent requests.

For detailed security specifications, see [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md).

---

## 🧪 Running Tests

The test suite requires no external dependencies and runs with Python's built-in `unittest`:

```bash
# Run full unit test suite
python -m unittest discover -s tests -t .
```

---

## 📦 Building Standalone Windows Executable

To compile a single-file executable for Windows with PyInstaller:

```cmd
cd AutoPilot-AI
scripts\build_windows_exe.bat
```

The resulting binary will be output to `dist\AutoPilot-AI.exe`.

---

## 🤝 Adding New Integrations

Developers can easily create and register new adapters for upcoming AI coding tools. Refer to [docs/CONTRIBUTING_ADAPTERS.md](docs/CONTRIBUTING_ADAPTERS.md) for full instructions and boilerplate examples.
