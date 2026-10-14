package com.example.viewmodel

import androidx.lifecycle.ViewModel
import com.example.engine.RuleEngine
import com.example.model.ActionCategory
import com.example.model.AgentCapability
import com.example.model.AgentInfo
import com.example.model.AgentRequest
import com.example.model.ApprovalEvent
import com.example.model.AutomationStatus
import com.example.model.DecisionOutcome
import com.example.model.EvaluationResult
import com.example.model.IntegrationLevel
import com.example.model.PermissionProfile
import com.example.model.RiskLevel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import java.util.UUID

enum class Screen {
    DASHBOARD,
    PENDING,
    RULES,
    HISTORY,
    AGENTS,
    SIMULATOR
}

data class AutoPilotUiState(
    val currentScreen: Screen = Screen.DASHBOARD,
    val automationStatus: AutomationStatus = AutomationStatus.ACTIVE,
    val isDryRun: Boolean = false,
    val activeProfile: PermissionProfile = RuleEngine.defaultBalancedProfile,
    val profiles: List<PermissionProfile> = listOf(
        RuleEngine.defaultBalancedProfile,
        RuleEngine.defaultManualProfile,
        RuleEngine.defaultCustomProfile
    ),
    val agents: List<AgentInfo> = emptyList(),
    val pendingRequests: List<AgentRequest> = emptyList(),
    val eventHistory: List<ApprovalEvent> = emptyList(),
    val showOnboarding: Boolean = false,
    val showEmergencyDialog: Boolean = false,
    val searchQuery: String = "",
    val selectedFilterOutcome: DecisionOutcome? = null
)

class AutoPilotViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(AutoPilotUiState())
    val uiState: StateFlow<AutoPilotUiState> = _uiState.asStateFlow()

    init {
        initAgents()
        initInitialData()
    }

    private fun initAgents() {
        val initialAgents = listOf(
            AgentInfo(
                id = "cursor",
                name = "Cursor",
                integrationLevel = IntegrationLevel.CONFIG_OVERRIDE,
                installed = true,
                running = true,
                version = "0.42.3",
                capabilities = listOf(
                    AgentCapability("Workspace .cursorrules Sync", true, "Syncs permissions to .cursorrules file"),
                    AgentCapability("Settings Inspection", true, "Reads configuration from user profile"),
                    AgentCapability("Terminal Command Detection", true, "Validates commands in integrated terminal"),
                    AgentCapability("Native Daemon Protocol", false, "Closed-source backend does not expose public daemon")
                ),
                limitations = listOf(
                    "Approvals rely on local workspace rules and verified window focus",
                    "Target window title must match Cursor before approval dispatch"
                ),
                health = "Healthy"
            ),
            AgentInfo(
                id = "claude_code",
                name = "Claude Code",
                integrationLevel = IntegrationLevel.CLI_WRAPPER,
                installed = true,
                running = true,
                version = "1.0.8",
                capabilities = listOf(
                    AgentCapability("Tool Permissions Sync", true, "Configures allowedTools in ~/.claude.json"),
                    AgentCapability("Interactive Stdin Prompt Hook", true, "Automates terminal confirmation prompts"),
                    AgentCapability("Bash Command Parsing", true, "Evaluates bash execution safety before approval")
                ),
                limitations = listOf(
                    "Requires active terminal session access to intercept stdin prompts",
                    "Config file updates require session reload"
                ),
                health = "Healthy"
            ),
            AgentInfo(
                id = "google_antigravity",
                name = "Google Antigravity",
                integrationLevel = IntegrationLevel.NATIVE_API,
                installed = true,
                running = false,
                version = "2.1.0-dev",
                capabilities = listOf(
                    AgentCapability("Agent Workspace Protocol Bridge", true, "Zero-click JSON-RPC permission handshake"),
                    AgentCapability("Workspace Sandboxing", true, "Enforces strict boundary constraints"),
                    AgentCapability("Batch Action Pre-check", true, "Evaluates multi-step agent plans in one pass")
                ),
                limitations = listOf(
                    "Requires local bridge socket connection; falls back to window verification when socket is inactive"
                ),
                health = "Idle"
            ),
            AgentInfo(
                id = "vscode_copilot",
                name = "VS Code (GitHub Copilot)",
                integrationLevel = IntegrationLevel.CONFIG_OVERRIDE,
                installed = true,
                running = true,
                version = "1.95.2",
                capabilities = listOf(
                    AgentCapability("Copilot Settings Audit", true, "Audits workspace and user settings"),
                    AgentCapability("Process & Editor Detection", true, "Identifies active VS Code windows and tasks"),
                    AgentCapability("Direct Extension Interop", false, "VS Code sandbox restricts external extension state access")
                ),
                limitations = listOf(
                    "VS Code extension sandbox prevents direct internal chat manipulation; uses settings policy & verified focus"
                ),
                health = "Healthy"
            )
        )
        _uiState.update { it.copy(agents = initialAgents) }
    }

    private fun initInitialData() {
        // Seed some realistic initial pending and history items for instant live UX
        val samplePending = listOf(
            AgentRequest(
                id = "req_101",
                agentId = "claude_code",
                agentName = "Claude Code",
                category = ActionCategory.PACKAGE_INSTALL,
                actionDescription = "Install production package 'axios'",
                command = "npm install axios@1.7.4",
                workspacePath = "/workspace/project"
            ),
            AgentRequest(
                id = "req_102",
                agentId = "cursor",
                agentName = "Cursor",
                category = ActionCategory.NETWORK_ACCESS,
                actionDescription = "Fetch external schema from remote API",
                command = "curl -s https://api.github.com/repos/owner/repo",
                workspacePath = "/workspace/project"
            )
        )

        val sampleEvents = listOf(
            ApprovalEvent(
                eventId = "ev_01",
                request = AgentRequest(
                    id = "req_01",
                    agentId = "claude_code",
                    agentName = "Claude Code",
                    category = ActionCategory.TEST_RUN,
                    actionDescription = "Run test suite",
                    command = "npm test",
                    workspacePath = "/workspace/project"
                ),
                evaluation = EvaluationResult(
                    outcome = DecisionOutcome.APPROVED,
                    reason = "Action safely evaluated and permitted by 'Balanced' profile rules.",
                    riskLevel = RiskLevel.SAFE,
                    matchedRule = "^npm (test|run lint|run build).*$",
                    autoApproved = true
                )
            ),
            ApprovalEvent(
                eventId = "ev_02",
                request = AgentRequest(
                    id = "req_02",
                    agentId = "cursor",
                    agentName = "Cursor",
                    category = ActionCategory.FILE_EDIT,
                    actionDescription = "Update component source",
                    filePath = "src/components/Header.tsx",
                    workspacePath = "/workspace/project"
                ),
                evaluation = EvaluationResult(
                    outcome = DecisionOutcome.APPROVED,
                    reason = "Action safely evaluated and permitted by 'Balanced' profile rules.",
                    riskLevel = RiskLevel.LOW,
                    matchedRule = "policy:balanced",
                    autoApproved = true
                )
            ),
            ApprovalEvent(
                eventId = "ev_03",
                request = AgentRequest(
                    id = "req_03",
                    agentId = "cursor",
                    agentName = "Cursor",
                    category = ActionCategory.FILE_DELETE,
                    actionDescription = "Purge directory",
                    command = "rm -rf /",
                    workspacePath = "/workspace/project"
                ),
                evaluation = EvaluationResult(
                    outcome = DecisionOutcome.DENIED,
                    reason = "Blocked for safety: Command matches critical destructive pattern",
                    riskLevel = RiskLevel.CRITICAL,
                    matchedRule = "security:critical_boundary",
                    autoApproved = false
                )
            )
        )

        _uiState.update {
            it.copy(
                pendingRequests = samplePending,
                eventHistory = sampleEvents
            )
        }
    }

    fun navigateTo(screen: Screen) {
        _uiState.update { it.copy(currentScreen = screen) }
    }

    fun setProfile(profileName: String) {
        val target = _uiState.value.profiles.firstOrNull { it.name.equals(profileName, ignoreCase = true) }
        if (target != null) {
            _uiState.update { it.copy(activeProfile = target) }
        }
    }

    fun toggleAutomation() {
        _uiState.update { state ->
            val next = when (state.automationStatus) {
                AutomationStatus.ACTIVE -> AutomationStatus.PAUSED
                AutomationStatus.PAUSED -> AutomationStatus.ACTIVE
                AutomationStatus.STOPPED -> AutomationStatus.ACTIVE
                AutomationStatus.EMERGENCY_STOP -> AutomationStatus.STOPPED
            }
            state.copy(automationStatus = next)
        }
    }

    fun toggleDryRun(enabled: Boolean) {
        _uiState.update { it.copy(isDryRun = enabled) }
    }

    fun triggerEmergencyStop() {
        val stopEvent = ApprovalEvent(
            eventId = UUID.randomUUID().toString().take(8),
            request = AgentRequest(
                id = "sys_halt",
                agentId = "system",
                agentName = "AutoPilot AI",
                category = ActionCategory.SENSITIVE_OP,
                actionDescription = "EMERGENCY STOP TRIGGERED BY USER"
            ),
            evaluation = EvaluationResult(
                outcome = DecisionOutcome.BLOCKED_EMERGENCY,
                reason = "Immediate emergency stop engaged. All automated approvals suspended.",
                riskLevel = RiskLevel.CRITICAL,
                matchedRule = "system:emergency_stop",
                autoApproved = false
            )
        )

        _uiState.update {
            it.copy(
                automationStatus = AutomationStatus.EMERGENCY_STOP,
                showEmergencyDialog = true,
                eventHistory = listOf(stopEvent) + it.eventHistory
            )
        }
    }

    fun dismissEmergencyDialog() {
        _uiState.update { it.copy(showEmergencyDialog = false) }
    }

    fun toggleOnboarding(show: Boolean) {
        _uiState.update { it.copy(showOnboarding = show) }
    }

    fun approvePending(requestId: String) {
        val req = _uiState.value.pendingRequests.find { it.id == requestId } ?: return
        val outcome = if (_uiState.value.isDryRun) DecisionOutcome.DRY_RUN_APPROVED else DecisionOutcome.APPROVED
        val event = ApprovalEvent(
            eventId = UUID.randomUUID().toString().take(8),
            request = req,
            evaluation = EvaluationResult(
                outcome = outcome,
                reason = "Explicitly approved by user from dashboard.",
                riskLevel = RiskLevel.LOW,
                matchedRule = "user_manual_approval",
                autoApproved = false
            )
        )

        _uiState.update { state ->
            state.copy(
                pendingRequests = state.pendingRequests.filterNot { it.id == requestId },
                eventHistory = listOf(event) + state.eventHistory
            )
        }
    }

    fun denyPending(requestId: String) {
        val req = _uiState.value.pendingRequests.find { it.id == requestId } ?: return
        val outcome = if (_uiState.value.isDryRun) DecisionOutcome.DRY_RUN_DENIED else DecisionOutcome.DENIED
        val event = ApprovalEvent(
            eventId = UUID.randomUUID().toString().take(8),
            request = req,
            evaluation = EvaluationResult(
                outcome = outcome,
                reason = "Explicitly denied by user from dashboard.",
                riskLevel = RiskLevel.LOW,
                matchedRule = "user_manual_denial",
                autoApproved = false
            )
        )

        _uiState.update { state ->
            state.copy(
                pendingRequests = state.pendingRequests.filterNot { it.id == requestId },
                eventHistory = listOf(event) + state.eventHistory
            )
        }
    }

    fun processSimulatedRequest(
        agentId: String,
        category: ActionCategory,
        command: String? = null,
        filePath: String? = null,
        actionDescription: String = "Simulated Request"
    ): ApprovalEvent {
        val agent = _uiState.value.agents.find { it.id == agentId }
        val req = AgentRequest(
            id = "sim_" + UUID.randomUUID().toString().take(6),
            agentId = agentId,
            agentName = agent?.name ?: "Unknown Agent",
            category = category,
            actionDescription = actionDescription,
            command = command,
            filePath = filePath,
            workspacePath = "/workspace/project"
        )

        val eval = when (_uiState.value.automationStatus) {
            AutomationStatus.EMERGENCY_STOP -> EvaluationResult(
                outcome = DecisionOutcome.BLOCKED_EMERGENCY,
                reason = "Emergency stop is engaged. AutoPilot AI is completely locked.",
                riskLevel = RiskLevel.CRITICAL,
                matchedRule = "system:emergency_stop",
                autoApproved = false
            )
            AutomationStatus.STOPPED, AutomationStatus.PAUSED -> EvaluationResult(
                outcome = DecisionOutcome.PENDING,
                reason = "Automation is ${_uiState.value.automationStatus.name.lowercase()}. Manual decision required.",
                riskLevel = RuleEngine.assessRisk(req).first,
                matchedRule = "system:paused",
                autoApproved = false
            )
            else -> {
                val evaluated = RuleEngine.evaluate(req, _uiState.value.activeProfile)
                if (_uiState.value.isDryRun && evaluated.outcome == DecisionOutcome.APPROVED) {
                    evaluated.copy(
                        outcome = DecisionOutcome.DRY_RUN_APPROVED,
                        reason = "[DRY-RUN] ${evaluated.reason}"
                    )
                } else if (_uiState.value.isDryRun && evaluated.outcome == DecisionOutcome.DENIED) {
                    evaluated.copy(
                        outcome = DecisionOutcome.DRY_RUN_DENIED,
                        reason = "[DRY-RUN] ${evaluated.reason}"
                    )
                } else evaluated
            }
        }

        val event = ApprovalEvent(
            eventId = UUID.randomUUID().toString().take(8),
            request = req,
            evaluation = eval
        )

        _uiState.update { state ->
            val updatedPending = if (eval.outcome == DecisionOutcome.PENDING) {
                listOf(req) + state.pendingRequests
            } else {
                state.pendingRequests
            }
            state.copy(
                pendingRequests = updatedPending,
                eventHistory = listOf(event) + state.eventHistory
            )
        }

        return event
    }

    fun updateSearchQuery(query: String) {
        _uiState.update { it.copy(searchQuery = query) }
    }

    fun setFilterOutcome(outcome: DecisionOutcome?) {
        _uiState.update { it.copy(selectedFilterOutcome = outcome) }
    }

    fun clearHistory() {
        _uiState.update { it.copy(eventHistory = emptyList()) }
    }
}
