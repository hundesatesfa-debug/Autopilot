from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from .models import PermissionProfile


class ConfigManager:
    """
    Manages AutoPilot AI configuration, profiles, and persistence.
    Maintains clean JSON configuration with automatic migrations and secure defaults.
    """

    DEFAULT_CONFIG: Dict[str, Any] = {
        "version": "1.0.0",
        "global_automation_enabled": True,
        "dry_run_mode": False,
        "active_profile": "balanced",
        "workspaces": ["."],
        "rate_limit_per_minute": 30,
        "notification_sound": True,
        "notification_desktop": True,
        "auto_pause_on_unknown": True,
        "adapters": {
            "cursor": {"enabled": True, "mode": "auto"},
            "claude_code": {"enabled": True, "mode": "auto"},
            "google_antigravity": {"enabled": True, "mode": "auto"},
            "vscode_copilot": {"enabled": True, "mode": "auto"},
        },
        "logging": {
            "level": "INFO",
            "log_to_file": True,
            "audit_trail": True,
            "redact_secrets": True,
        },
    }

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self.config_dir = Path(config_dir).resolve()
        else:
            # Prefer ~/.autopilot_ai, with fallback to local ./config
            user_home = Path.home()
            self.config_dir = user_home / ".autopilot_ai"

        self.config_file = self.config_dir / "config.json"
        self.profiles_file = self.config_dir / "profiles.json"
        self.config: Dict[str, Any] = dict(self.DEFAULT_CONFIG)
        self.profiles: Dict[str, PermissionProfile] = {}

        self.ensure_initialized()

    def ensure_initialized(self) -> None:
        """Create config directory and default configuration if absent."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if not self.profiles_file.exists():
            self._write_default_profiles()
        else:
            self.load_profiles()

        if not self.config_file.exists():
            self.save_config()
        else:
            self.load_config()

    def _write_default_profiles(self) -> None:
        """Initialize built-in profiles: manual, balanced, and custom."""
        from .permission_engine import PermissionEngine

        balanced = PermissionEngine._create_default_balanced_profile()
        manual = PermissionProfile(
            name="Manual",
            description="All approval decisions remain strictly with the user. Zero automatic approvals.",
            auto_approve_categories=[],
            allowed_commands=[],
            blocked_commands=[".*"],
            allowed_path_patterns=[],
            blocked_path_patterns=[".*"],
            require_workspace_containment=True,
            allow_network=False,
            allow_package_install=False,
        )
        custom = PermissionProfile(
            name="Custom",
            description="User-configured policy tailored for specific projects and workflows.",
            auto_approve_categories=["file_create", "file_edit", "test_run"],
            allowed_commands=["^pytest.*$", "^npm test.*$"],
            blocked_commands=[r".*(rm|del)\s+(-rf|/s).*", r".*(sudo|runas).*"],
            allowed_path_patterns=["^src/.*$", "^tests/.*$"],
            blocked_path_patterns=[r".*\.env.*"],
            require_workspace_containment=True,
            allow_network=False,
            allow_package_install=False,
        )

        self.profiles = {
            "manual": manual,
            "balanced": balanced,
            "custom": custom,
        }
        self.save_profiles()

    def load_profiles(self) -> None:
        try:
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.profiles = {k: PermissionProfile.from_dict(v) for k, v in data.items()}
        except Exception:
            self._write_default_profiles()

    def save_profiles(self) -> None:
        try:
            data = {k: v.to_dict() for k, v in self.profiles.items()}
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")

    def load_config(self) -> None:
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.config = {**self.DEFAULT_CONFIG, **data}
        except Exception:
            self.config = dict(self.DEFAULT_CONFIG)
            self.save_config()

    def save_config(self) -> None:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_active_profile(self) -> PermissionProfile:
        name = self.config.get("active_profile", "balanced").lower()
        if name in self.profiles:
            return self.profiles[name]
        return self.profiles.get("balanced") or list(self.profiles.values())[0]

    def set_active_profile(self, profile_name: str) -> bool:
        key = profile_name.lower()
        if key in self.profiles:
            self.config["active_profile"] = key
            self.save_config()
            return True
        return False

    def is_global_automation_enabled(self) -> bool:
        return bool(self.config.get("global_automation_enabled", True))

    def set_global_automation_enabled(self, enabled: bool) -> None:
        self.config["global_automation_enabled"] = enabled
        self.save_config()

    def is_dry_run_mode(self) -> bool:
        return bool(self.config.get("dry_run_mode", False))

    def set_dry_run_mode(self, enabled: bool) -> None:
        self.config["dry_run_mode"] = enabled
        self.save_config()

    def add_workspace(self, workspace_path: str) -> None:
        resolved = str(Path(workspace_path).resolve())
        workspaces = self.config.setdefault("workspaces", [])
        if resolved not in workspaces:
            workspaces.append(resolved)
            self.save_config()

    def get_workspaces(self) -> List[str]:
        return self.config.get("workspaces", ["."])
