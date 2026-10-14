# AutoPilot AI Security Model & Threat Mitigation

AutoPilot AI is engineered according to the principle of least privilege and defense in depth. It functions as a local security boundary between autonomous coding agents and the developer's workstation.

---

## 1. Threat Vectors Addressed

| Threat | Attack Vector | AutoPilot AI Mitigation |
| :--- | :--- | :--- |
| **Accidental System Destruction** | Agent runs `rm -rf /` or `del /s /q C:\*` | Critical command regex filters block execution immediately regardless of profile settings. |
| **Directory Traversal** | Agent touches files via `../../etc/passwd` or outside the repo | Strict path resolution (`Path.resolve()`) verifies containment within designated workspace root. |
| **Credential / Secret Exfiltration** | Agent reads `.env`, `~/.ssh/id_rsa`, or tokens | Restricted file patterns hold any sensitive file access for manual approval. |
| **Privilege Escalation** | Agent executes `sudo`, `runas`, or `chmod 777` | Administrative privilege requests are classified as `CRITICAL` risk and blocked. |
| **Remote Code Injection** | Agent pipes untrusted web content: `curl ... \| bash` | Regex checks flag remote shell execution pipes as critical security violations. |
| **Infinite Approval Loops** | Agent rapidly triggers repetitive approval prompts | Rate limiter caps automated approvals per minute (default: 30/min). |
| **False Positive Dialogs** | Generic window with "Approve" label | Action payload is evaluated; dialog text alone never causes approval. |

---

## 2. Permission Profiles

### Manual Profile
- Zero automatic approvals.
- Every single agent action remains pending for explicit user confirmation.

### Balanced Profile (Default)
- **Auto-Permitted:**
  - File creation and edits strictly within authorized workspace roots.
  - Safe test suites (`pytest`, `npm test`, `cargo test`, `go test`).
  - Safe builds and linters (`npm run build`, `ruff check`, `black`, `prettier`).
- **Always Held Pending:**
  - File deletions.
  - Dependency installations (`npm install`, `pip install`).
  - Network requests.
  - Operations outside workspace roots.
  - Untrusted or unknown commands.

### Custom Profile
- User defines exact allowed/blocked regexes for commands and file paths.
- Workspace containment remains enforced by default.

---

## 3. Immediate Emergency Stop
The Emergency Stop button engages an irreversible runtime lock. While engaged:
- No approvals can be dispatched.
- All incoming requests are marked `BLOCKED_EMERGENCY`.
- Re-enabling automation requires explicit user confirmation.
