from __future__ import annotations

import json
import os
import re
import time
from collections import deque
from pathlib import Path
from typing import List, Dict, Any, Optional
from .models import ApprovalEvent, DecisionOutcome, RiskLevel


class EventLogger:
    """
    Manages local audit logging and event tracking for AutoPilot AI.
    Ensures zero cloud leakage, enforces sensitive data redaction,
    and supports rich log queries.
    """

    REDACTION_PATTERNS = [
        (re.compile(r"(api[_-]?key|secret|token|password|auth|bearer)\s*[:=\s]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?", re.IGNORECASE), r"\1=***REDACTED***"),
        (re.compile(r"\bBearer\s+([a-zA-Z0-9_\-\.]{8,})", re.IGNORECASE), r"Bearer ***REDACTED***"),
        (re.compile(r"(AIza[0-9A-Za-z-_]{35})"), r"***REDACTED_API_KEY***"),
        (re.compile(r"(ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})"), r"***REDACTED_GITHUB_TOKEN***"),
        (re.compile(r"(sk-[a-zA-Z0-9]{32,})"), r"***REDACTED_SECRET_KEY***"),
    ]

    def __init__(self, log_dir: Optional[str] = None, max_memory_events: int = 500):
        if log_dir:
            self.log_dir = Path(log_dir).resolve()
        else:
            self.log_dir = Path.home() / ".autopilot_ai" / "logs"

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit.jsonl"
        self.text_log_file = self.log_dir / "activity.log"
        self._recent_events: deque[ApprovalEvent] = deque(maxlen=max_memory_events)

    def redact(self, text: Optional[str]) -> Optional[str]:
        """Redact known API keys, tokens, and sensitive query strings."""
        if not text:
            return text
        sanitized = text
        for pattern, replacement in self.REDACTION_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def log_event(self, event: ApprovalEvent) -> None:
        """Sanitize and record an approval event to in-memory cache, JSONL audit file, and text log."""
        # Redact potentially sensitive content in command or file path
        if event.request.command:
            event.request.command = self.redact(event.request.command)
        if event.request.file_path:
            event.request.file_path = self.redact(event.request.file_path)

        self._recent_events.appendleft(event)

        # Write to JSONL audit file
        try:
            with open(self.audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception as e:
            print(f"Warning: Failed to write to audit log: {e}")

        # Write human-readable entry to text log
        try:
            readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event.timestamp))
            agent = event.request.agent_name
            cat = event.request.category.value
            outcome = event.evaluation.outcome.value
            risk = event.evaluation.risk_level.value
            desc = event.request.action_description or event.request.command or event.request.file_path or "Action"
            reason = event.evaluation.reason

            line = f"[{readable_time}] [{outcome.upper():<10}] [{risk.upper():<8}] [{agent}] ({cat}) {desc} -> {reason}\n"
            with open(self.text_log_file, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            print(f"Warning: Failed to write to text log: {e}")

    def get_recent_events(self, limit: int = 50) -> List[ApprovalEvent]:
        """Get recent in-memory events."""
        return list(self._recent_events)[:limit]

    def query(
        self,
        agent_id: Optional[str] = None,
        outcome: Optional[DecisionOutcome] = None,
        min_risk: Optional[RiskLevel] = None,
        limit: int = 100,
    ) -> List[ApprovalEvent]:
        """Query recent events with filters."""
        results: List[ApprovalEvent] = []
        for event in self._recent_events:
            if agent_id and event.request.agent_id != agent_id:
                continue
            if outcome and event.evaluation.outcome != outcome:
                continue
            if min_risk:
                # Filter by risk hierarchy
                risk_order = [RiskLevel.SAFE, RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
                if risk_order.index(event.evaluation.risk_level) < risk_order.index(min_risk):
                    continue
            results.append(event)
            if len(results) >= limit:
                break
        return results

    def clear_logs(self) -> None:
        """Clear log buffers and archive files."""
        self._recent_events.clear()
        if self.audit_file.exists():
            self.audit_file.write_text("", encoding="utf-8")
        if self.text_log_file.exists():
            self.text_log_file.write_text("", encoding="utf-8")
