package com.example.model

enum class ActionCategory(val displayName: String) {
    FILE_CREATE("File Create"),
    FILE_EDIT("File Edit"),
    TEST_RUN("Test Execution"),
    BUILD_RUN("Build Execution"),
    PACKAGE_INSTALL("Package Install"),
    NETWORK_ACCESS("Network Access"),
    FILE_DELETE("File Delete"),
    ADMIN_PRIVILEGES("Admin / Sudo"),
    SENSITIVE_OP("Sensitive Operation"),
    UNKNOWN("Unknown Action")
}

enum class RiskLevel {
    SAFE, LOW, MEDIUM, HIGH, CRITICAL
}

enum class DecisionOutcome {
    APPROVED, DENIED, PENDING, BLOCKED_EMERGENCY, DRY_RUN_APPROVED, DRY_RUN_DENIED
}

enum class IntegrationLevel(val label: String) {
    NATIVE_API("Native Protocol"),
    CONFIG_OVERRIDE("Settings / Config"),
    CLI_WRAPPER("CLI Hook / Stdin"),
    WINDOW_ACCESSIBILITY("Window Verification"),
    UNSUPPORTED("Unsupported")
}

enum class AutomationStatus {
    ACTIVE, PAUSED, STOPPED, EMERGENCY_STOP
}

data class AgentCapability(
    val name: String,
    val supported: Boolean,
    val description: String
)

data class AgentInfo(
    val id: String,
    val name: String,
    val integrationLevel: IntegrationLevel,
    val installed: Boolean,
    val running: Boolean,
    val version: String,
    val capabilities: List<AgentCapability>,
    val limitations: List<String>,
    val health: String
)

data class AgentRequest(
    val id: String,
    val agentId: String,
    val agentName: String,
    val category: ActionCategory,
    val actionDescription: String,
    val command: String? = null,
    val filePath: String? = null,
    val workspacePath: String = "/workspace/project",
    val timestamp: Long = System.currentTimeMillis()
)

data class EvaluationResult(
    val outcome: DecisionOutcome,
    val reason: String,
    val riskLevel: RiskLevel,
    val matchedRule: String? = null,
    val autoApproved: Boolean = false,
    val timestamp: Long = System.currentTimeMillis()
)

data class ApprovalEvent(
    val eventId: String,
    val request: AgentRequest,
    val evaluation: EvaluationResult,
    val timestamp: Long = System.currentTimeMillis()
)

data class PermissionProfile(
    val name: String,
    val description: String,
    val autoApproveCategories: Set<ActionCategory>,
    val allowedCommandRegexes: List<String>,
    val blockedCommandRegexes: List<String>,
    val allowedPathPatterns: List<String>,
    val blockedPathPatterns: List<String>,
    val requireWorkspaceContainment: Boolean = true,
    val allowNetwork: Boolean = false,
    val allowPackageInstall: Boolean = false
)
