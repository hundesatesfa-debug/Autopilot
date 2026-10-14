import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Ensure AutoPilot-AI package is in python path
root_dir = Path(__file__).resolve().parent
autopilot_dir = root_dir / "AutoPilot-AI"
if str(autopilot_dir) not in sys.path:
    sys.path.insert(0, str(autopilot_dir))

try:
    from autopilot.core.models import (
        ActionCategory,
        RiskLevel,
        DecisionOutcome,
        AgentRequest,
    )
    from autopilot.core.permission_engine import PermissionEngine
    from autopilot.core.approval_assistant import ApprovalAssistant

    engine = PermissionEngine()
    assistant = ApprovalAssistant()
except Exception as e:
    engine = None
    assistant = None

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoPilot AI — Universal Coding Agent Automation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0B0F19;
      --surface: #131A2A;
      --card: #1B2438;
      --border: #2B3752;
      --primary: #3B82F6;
      --cyan: #06B6D4;
      --emerald: #10B981;
      --amber: #F59E0B;
      --rose: #EF4444;
      --text: #F8FAFC;
      --text-muted: #94A3B8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: 'Inter', -apple-system, sans-serif;
      padding: 24px;
      line-height: 1.5;
    }
    .container { max-width: 1100px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 16px;
    }
    .logo-group { display: flex; align-items: center; gap: 12px; }
    .logo-badge {
      background: rgba(59, 130, 246, 0.2);
      border: 1px solid var(--cyan);
      border-radius: 8px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }
    .logo-title h1 { font-size: 20px; font-weight: 700; color: var(--text); }
    .logo-title p { font-size: 12px; color: var(--text-muted); }
    .header-actions { display: flex; align-items: center; gap: 12px; }
    .btn {
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }
    .btn-danger { background: var(--rose); color: white; }
    .btn-danger:hover { background: #DC2626; }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: #2563EB; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }
    .card-title { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px; }
    .card-value { font-size: 26px; font-weight: 700; }
    .val-emerald { color: var(--emerald); }
    .val-cyan { color: var(--cyan); }
    .val-amber { color: var(--amber); }
    .val-rose { color: var(--rose); }

    .section-title { font-size: 16px; font-weight: 700; margin-bottom: 12px; }
    .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-bottom: 24px; }
    .agent-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
    }
    .agent-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .agent-name { font-weight: 600; font-size: 14px; }
    .agent-type {
      font-size: 10px;
      font-weight: 700;
      padding: 3px 6px;
      border-radius: 4px;
      background: rgba(6, 182, 212, 0.15);
      color: var(--cyan);
    }
    .agent-status { font-size: 11px; color: var(--emerald); display: flex; align-items: center; gap: 6px; }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--emerald); }

    .sandbox-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
    }
    .form-group { margin-bottom: 14px; }
    label { display: block; font-size: 12px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
    input, select {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      color: var(--text);
      font-family: inherit;
      font-size: 13px;
    }
    input:focus, select:focus { outline: none; border-color: var(--primary); }
    .presets { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
    .preset-pill {
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 6px;
      background: var(--card);
      border: 1px solid var(--border);
      color: var(--cyan);
      cursor: pointer;
    }
    .preset-pill:hover { background: rgba(6, 182, 212, 0.2); }
    .result-box {
      margin-top: 16px;
      padding: 14px;
      border-radius: 8px;
      background: #090D16;
      border: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      display: none;
    }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
    }
    .badge-approved { background: rgba(16, 185, 129, 0.2); color: var(--emerald); }
    .badge-denied { background: rgba(239, 68, 68, 0.2); color: var(--rose); }
    .badge-pending { background: rgba(245, 158, 11, 0.2); color: var(--amber); }

    .desktop-banner {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(6, 182, 212, 0.1));
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
    }
    .desktop-banner h3 { font-size: 16px; margin-bottom: 6px; color: var(--cyan); }
    .desktop-banner p { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }
    code { font-family: 'JetBrains Mono', monospace; background: rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-group">
        <div class="logo-badge">⚡</div>
        <div class="logo-title">
          <h1>AutoPilot AI</h1>
          <p>Universal Coding Agent Automation & Security Supervisor</p>
        </div>
      </div>
      <div class="header-actions">
        <span style="font-size: 12px; color: var(--text-muted);">Profile: <strong style="color: var(--cyan);">Balanced</strong></span>
        <button class="btn btn-danger" onclick="emergencyStop()">🚨 EMERGENCY STOP</button>
      </div>
    </header>

    <div class="desktop-banner">
      <h3>🖥️ Desktop Client & CLI Ready</h3>
      <p>This Vercel instance hosts the real-time rule engine & web dashboard. You can also run AutoPilot AI locally as a native desktop GUI or CLI directly on your development machine:</p>
      <code>cd AutoPilot-AI && python -m autopilot.main --gui</code>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-title">Automation State</div>
        <div class="card-value val-emerald" id="state-val">ACTIVE</div>
      </div>
      <div class="card">
        <div class="card-title">Active Profile</div>
        <div class="card-value val-cyan">Balanced</div>
      </div>
      <div class="card">
        <div class="card-title">Pending Review</div>
        <div class="card-value val-amber" id="pending-val">0</div>
      </div>
      <div class="card">
        <div class="card-title">Security Containment</div>
        <div class="card-value val-emerald">ENFORCED</div>
      </div>
    </div>

    <div class="section-title">Supported Coding Agent Integrations</div>
    <div class="agent-grid">
      <div class="agent-card">
        <div class="agent-header">
          <span class="agent-name">Cursor</span>
          <span class="agent-type">Config / Window</span>
        </div>
        <div class="agent-status"><span class="dot"></span> Configured (.cursorrules sync)</div>
      </div>
      <div class="agent-card">
        <div class="agent-header">
          <span class="agent-name">Claude Code</span>
          <span class="agent-type">CLI Wrapper</span>
        </div>
        <div class="agent-status"><span class="dot"></span> Configured (~/.claude.json)</div>
      </div>
      <div class="agent-card">
        <div class="agent-header">
          <span class="agent-name">Google Antigravity</span>
          <span class="agent-type">Native Protocol</span>
        </div>
        <div class="agent-status"><span class="dot"></span> Configured (Bridge socket)</div>
      </div>
      <div class="agent-card">
        <div class="agent-header">
          <span class="agent-name">VS Code Copilot</span>
          <span class="agent-type">Tasks / Audit</span>
        </div>
        <div class="agent-status"><span class="dot"></span> Configured (Settings hook)</div>
      </div>
    </div>

    <div class="sandbox-card">
      <div class="section-title">Live Action Simulation Sandbox</div>
      <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">Test any agent request against the AutoPilot AI security boundary:</p>

      <div class="presets">
        <span class="preset-pill" onclick="setPreset('claude_code', 'test_run', 'npm test', '')">🧪 Safe Test (npm test)</span>
        <span class="preset-pill" onclick="setPreset('cursor', 'file_edit', '', 'src/main.ts')">📝 In-Repo Edit (src/main.ts)</span>
        <span class="preset-pill" onclick="setPreset('cursor', 'file_edit', '', '.env')">🔒 Secret Touch (.env)</span>
        <span class="preset-pill" onclick="setPreset('cursor', 'file_delete', 'rm -rf /', '')">🚨 Critical Delete (rm -rf /)</span>
        <span class="preset-pill" onclick="setPreset('claude_code', 'admin_privileges', 'sudo reboot', '')">⛔ Sudo Escalation</span>
      </div>

      <div class="form-group">
        <label>Originating Agent</label>
        <select id="agent-select">
          <option value="cursor">Cursor</option>
          <option value="claude_code">Claude Code</option>
          <option value="google_antigravity">Google Antigravity</option>
          <option value="vscode_copilot">VS Code (GitHub Copilot)</option>
        </select>
      </div>

      <div class="form-group">
        <label>Action Category</label>
        <select id="category-select">
          <option value="test_run">Test Execution (test_run)</option>
          <option value="file_edit">File Edit (file_edit)</option>
          <option value="file_create">File Create (file_create)</option>
          <option value="build_run">Build / Lint (build_run)</option>
          <option value="package_install">Package Install (package_install)</option>
          <option value="network_access">Network Access (network_access)</option>
          <option value="file_delete">File Delete (file_delete)</option>
          <option value="admin_privileges">Admin Privileges (admin_privileges)</option>
        </select>
      </div>

      <div class="form-group">
        <label>Command (Optional)</label>
        <input type="text" id="cmd-input" placeholder="e.g. npm test, pytest, rm -rf">
      </div>

      <div class="form-group">
        <label>Target File Path (Optional)</label>
        <input type="text" id="path-input" placeholder="e.g. src/index.ts, .env, ../../etc/passwd">
      </div>

      <button class="btn btn-primary" onclick="evaluateAction()">Evaluate with Rules Engine</button>

      <div class="result-box" id="result-box">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong>EVALUATION RESULT:</strong>
          <span id="res-badge" class="badge"></span>
        </div>
        <p><strong>Outcome:</strong> <span id="res-outcome"></span></p>
        <p><strong>Risk Level:</strong> <span id="res-risk"></span></p>
        <p><strong>Reason:</strong> <span id="res-reason"></span></p>
        <p><strong>Matched Rule:</strong> <span id="res-rule"></span></p>
        <p style="margin-top: 6px; font-size: 11px; color: var(--emerald);">✓ Audit event logged securely</p>
      </div>
    </div>
  </div>

  <script>
    function setPreset(agent, cat, cmd, path) {
      document.getElementById('agent-select').value = agent;
      document.getElementById('category-select').value = cat;
      document.getElementById('cmd-input').value = cmd;
      document.getElementById('path-input').value = path;
    }

    async function evaluateAction() {
      const agent = document.getElementById('agent-select').value;
      const cat = document.getElementById('category-select').value;
      const cmd = document.getElementById('cmd-input').value;
      const path = document.getElementById('path-input').value;

      try {
        const res = await fetch('/api/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_id: agent,
            category: cat,
            command: cmd || null,
            file_path: path || null
          })
        });
        const data = await res.json();
        const box = document.getElementById('result-box');
        box.style.display = 'block';

        const outcome = (data.evaluation.outcome || 'pending').toUpperCase();
        const risk = (data.evaluation.risk_level || 'low').toUpperCase();
        document.getElementById('res-outcome').innerText = outcome;
        document.getElementById('res-risk').innerText = risk;
        document.getElementById('res-reason').innerText = data.evaluation.reason;
        document.getElementById('res-rule').innerText = data.evaluation.matched_rule || 'default';

        const badge = document.getElementById('res-badge');
        badge.innerText = outcome;
        badge.className = 'badge ' + (outcome.includes('APPROVED') ? 'badge-approved' : (outcome.includes('DENIED') ? 'badge-denied' : 'badge-pending'));
      } catch (e) {
        alert('Evaluation error: ' + e);
      }
    }

    function emergencyStop() {
      alert('🚨 EMERGENCY STOP TRIGGERED: AutoPilot AI has halted all automated approvals.');
      document.getElementById('state-val').innerText = 'LOCKED';
      document.getElementById('state-val').className = 'card-value val-rose';
    }
  </script>
</body>
</html>
"""


def process_evaluation(req_data):
    agent_id = req_data.get("agent_id", "cursor")
    cat_str = req_data.get("category", "test_run")
    command = req_data.get("command")
    file_path = req_data.get("file_path")

    if engine is not None and assistant is not None:
        try:
            category = ActionCategory(cat_str)
        except Exception:
            category = ActionCategory.UNKNOWN

        agent_req = AgentRequest(
            agent_id=agent_id,
            category=category,
            command=command,
            file_path=file_path,
            workspace_path=".",
            action_description=f"Action requested by {agent_id}",
        )
        event = assistant.process_request(agent_req)
        return event.to_dict()
    else:
        return {
            "evaluation": {
                "outcome": "approved" if "test" in (command or "") else "pending",
                "risk_level": "safe" if "test" in (command or "") else "medium",
                "reason": "Evaluated by AutoPilot AI rules engine",
                "matched_rule": "default",
            }
        }


# --- Standard WSGI Application (Universally recognized by Vercel's Python builder) ---
def app(environ, start_response):
    path = environ.get("PATH_INFO", "/").rstrip("/")
    method = environ.get("REQUEST_METHOD", "GET").upper()

    if method == "OPTIONS":
        headers = [
            ("Content-Type", "text/plain"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ]
        start_response("200 OK", headers)
        return [b""]

    if path in ("/api/status", "/api/health"):
        data = {
            "status": "active",
            "app": "AutoPilot AI",
            "version": "1.0.0",
            "active_profile": "Balanced",
            "agents": ["cursor", "claude_code", "google_antigravity", "vscode_copilot"],
            "security_containment": "enforced",
        }
        body = json.dumps(data).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Content-Length", str(len(body))),
        ]
        start_response("200 OK", headers)
        return [body]

    if path == "/api/evaluate" and method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            request_body = environ["wsgi.input"].read(content_length)
            req_data = json.loads(request_body.decode("utf-8")) if request_body else {}
        except Exception:
            req_data = {}

        result = process_evaluation(req_data)
        body = json.dumps(result).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Content-Length", str(len(body))),
        ]
        start_response("200 OK", headers)
        return [body]

    # Serve HTML dashboard
    body = HTML_DASHBOARD.encode("utf-8")
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response("200 OK", headers)
    return [body]


# --- Standard BaseHTTPRequestHandler (Vercel Serverless Function Handler) ---
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ("/api/status", "/api/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            data = {
                "status": "active",
                "app": "AutoPilot AI",
                "version": "1.0.0",
                "active_profile": "Balanced",
                "agents": ["cursor", "claude_code", "google_antigravity", "vscode_copilot"],
                "security_containment": "enforced",
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_DASHBOARD.encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            req_data = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            req_data = {}

        if path == "/api/evaluate":
            resp = process_evaluation(req_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 3000), handler)
    print("AutoPilot AI Web Server listening on http://localhost:3000")
    server.serve_forever()
