package com.example.engine

import com.example.model.ActionCategory
import com.example.model.AgentRequest
import com.example.model.DecisionOutcome
import com.example.model.EvaluationResult
import com.example.model.PermissionProfile
import com.example.model.RiskLevel
import java.io.File
import java.util.regex.Pattern

object RuleEngine {

    val defaultBalancedProfile = PermissionProfile(
        name = "Balanced",
        description = "Automates routine low-risk actions (workspace file edits, tests, builds) while strictly confirming deletions, installs, and network commands.",
        autoApproveCategories = setOf(
            ActionCategory.FILE_CREATE,
            ActionCategory.FILE_EDIT,
            ActionCategory.TEST_RUN,
            ActionCategory.BUILD_RUN
        ),
        allowedCommandRegexes = listOf(
            "^npm (test|run lint|run build|run format|run typecheck).*$",
            "^pytest( .*)?$",
            "^python -m unittest( .*)?$",
            "^cargo (test|check|build|clippy).*$",
            "^go (test|build|vet).*$",
            "^git (status|diff|log|branch).*$",
            "^ruff (check|format).*$",
            "^black( .*)?$",
            "^prettier( .*)?$"
        ),
        blockedCommandRegexes = listOf(
            ".*(rm|del|erase)\\s+(-r|-rf|-f|/s|/q).*",
            ".*(sudo|su|runas|chmod|chown).*",
            ".*(curl|wget|Invoke-WebRequest|iwr).*\\|.*(sh|bash|powershell|cmd).*",
            ".*(\\bformat\\b|\\bmkfs\\b|\\bdd\\b).*",
            ".*(\\.ssh|id_rsa|\\.env|id_ed25519|credentials).*",
            ".*(net user|net localgroup|reg add|reg delete).*"
        ),
        allowedPathPatterns = listOf(
            "^src/.*$",
            "^app/.*$",
            "^lib/.*$",
            "^tests?/.*$",
            "^docs/.*$",
            "^[a-zA-Z0-9_\\-\\.]+\\.(ts|tsx|js|jsx|py|rs|go|kt|java|cpp|c|h|json|md|yaml|yml|css|html|xml|toml)$"
        ),
        blockedPathPatterns = listOf(
            ".*\\.env.*",
            ".*\\.git/.*",
            ".*id_rsa.*",
            ".*credentials.*",
            ".*passwd.*",
            "^/etc/.*",
            "^[A-Za-z]:[\\\\/](Windows|Program Files).*"
        ),
        requireWorkspaceContainment = true,
        allowNetwork = false,
        allowPackageInstall = false
    )

    val defaultManualProfile = PermissionProfile(
        name = "Manual",
        description = "Zero automated approvals. Every action requires explicit manual user approval.",
        autoApproveCategories = emptySet(),
        allowedCommandRegexes = emptyList(),
        blockedCommandRegexes = listOf(".*"),
        allowedPathPatterns = emptyList(),
        blockedPathPatterns = listOf(".*"),
        requireWorkspaceContainment = true,
        allowNetwork = false,
        allowPackageInstall = false
    )

    val defaultCustomProfile = PermissionProfile(
        name = "Custom",
        description = "Tailored policies for advanced developer workflows.",
        autoApproveCategories = setOf(
            ActionCategory.FILE_CREATE,
            ActionCategory.FILE_EDIT,
            ActionCategory.TEST_RUN
        ),
        allowedCommandRegexes = listOf(
            "^pytest.*$",
            "^npm test.*$",
            "^git status.*$"
        ),
        blockedCommandRegexes = listOf(
            ".*(rm|del)\\s+(-rf|/s).*",
            ".*(sudo|runas).*"
        ),
        allowedPathPatterns = listOf("^src/.*$", "^tests/.*$"),
        blockedPathPatterns = listOf(".*\\.env.*"),
        requireWorkspaceContainment = true,
        allowNetwork = false,
        allowPackageInstall = false
    )

    private val criticalCommandPatterns = listOf(
        Pattern.compile("\\b(rm|del|erase|rmdir|rd)\\s+(-[a-zA-Z]*[rf]|/s|/q)\\b", Pattern.CASE_INSENSITIVE),
        Pattern.compile("\\b(format|mkfs|dd|diskpart|fdisk)\\b", Pattern.CASE_INSENSITIVE),
        Pattern.compile("\\b(sudo|su|runas|doas)\\b", Pattern.CASE_INSENSITIVE),
        Pattern.compile("\\b(chmod\\s+777|chmod\\s+-R\\s+777|chown)\\b", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(curl|wget|Invoke-WebRequest|iwr|Invoke-Expression|iex).*[\\|;]\\s*(sh|bash|powershell|cmd)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(\\.ssh[/\\\\]id_|\\.aws[/\\\\]credentials|\\.kube[/\\\\]config|\\.env\\b)", Pattern.CASE_INSENSITIVE)
    )

    private val sensitivePathPatterns = listOf(
        Pattern.compile("(^|[/\\\\])\\.env($|\\..*)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(^|[/\\\\])\\.git([/\\\\]|$)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(^|[/\\\\])\\.ssh([/\\\\]|$)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("(^|[/\\\\])(id_rsa|id_ed25519)($|\\..*)", Pattern.CASE_INSENSITIVE),
        Pattern.compile("^/etc/(passwd|shadow|sudoers)", Pattern.CASE_INSENSITIVE)
    )

    fun isPathWithinWorkspace(targetPath: String, workspaceRoot: String): Boolean {
        if (targetPath.isBlank() || workspaceRoot.isBlank()) return false
        return try {
            val ws = File(workspaceRoot).canonicalFile
            val target = if (File(targetPath).isAbsolute) {
                File(targetPath).canonicalFile
            } else {
                File(ws, targetPath).canonicalFile
            }
            target.path.startsWith(ws.path)
        } catch (e: Exception) {
            false
        }
    }

    fun assessRisk(request: AgentRequest): Pair<RiskLevel, String?> {
        // Critical command check first
        request.command?.let { cmd ->
            for (p in criticalCommandPatterns) {
                if (p.matcher(cmd).find()) {
                    return RiskLevel.CRITICAL to "Command matches critical destructive pattern: '${p.pattern()}'"
                }
            }
        }

        if (request.category == ActionCategory.ADMIN_PRIVILEGES || request.category == ActionCategory.SENSITIVE_OP) {
            return RiskLevel.CRITICAL to "Action requests elevated permissions (${request.category.displayName})"
        }

        if (request.category == ActionCategory.FILE_DELETE) {
            return RiskLevel.HIGH to "File deletion is a destructive operation"
        }

        // Sensitive paths
        request.filePath?.let { fp ->
            for (p in sensitivePathPatterns) {
                if (p.matcher(fp).find()) {
                    return RiskLevel.HIGH to "File path touches sensitive pattern: '$fp'"
                }
            }
            if (!isPathWithinWorkspace(fp, request.workspacePath)) {
                return RiskLevel.HIGH to "Target path '$fp' escapes workspace bounds"
            }
        }

        return when (request.category) {
            ActionCategory.FILE_CREATE, ActionCategory.FILE_EDIT -> RiskLevel.LOW to null
            ActionCategory.TEST_RUN, ActionCategory.BUILD_RUN -> RiskLevel.SAFE to null
            ActionCategory.PACKAGE_INSTALL, ActionCategory.NETWORK_ACCESS -> RiskLevel.MEDIUM to "Modifies external packages/network"
            else -> RiskLevel.LOW to null
        }
    }

    fun evaluate(request: AgentRequest, profile: PermissionProfile): EvaluationResult {
        val (risk, riskReason) = assessRisk(request)

        // Manual profile always holds pending
        if (profile.name.equals("Manual", ignoreCase = true)) {
            return EvaluationResult(
                outcome = DecisionOutcome.PENDING,
                reason = "Manual profile active: explicit user approval required.",
                riskLevel = risk,
                matchedRule = "profile:manual",
                autoApproved = false
            )
        }

        // Critical hard block
        if (risk == RiskLevel.CRITICAL) {
            return EvaluationResult(
                outcome = DecisionOutcome.DENIED,
                reason = "Blocked for safety: ${riskReason ?: "Critical boundary violation"}",
                riskLevel = risk,
                matchedRule = "security:critical_boundary",
                autoApproved = false
            )
        }

        // Workspace boundary containment check
        if (profile.requireWorkspaceContainment && request.filePath != null) {
            if (!isPathWithinWorkspace(request.filePath, request.workspacePath)) {
                return EvaluationResult(
                    outcome = DecisionOutcome.PENDING,
                    reason = "Target path '${request.filePath}' is outside workspace. Manual confirmation required.",
                    riskLevel = RiskLevel.HIGH,
                    matchedRule = "policy:workspace_containment",
                    autoApproved = false
                )
            }
        }

        // Blocked command check
        request.command?.let { cmd ->
            for (pat in profile.blockedCommandRegexes) {
                if (Pattern.compile(pat, Pattern.CASE_INSENSITIVE).matcher(cmd).find()) {
                    return EvaluationResult(
                        outcome = DecisionOutcome.DENIED,
                        reason = "Command matches blocked pattern: '$pat'",
                        riskLevel = RiskLevel.HIGH,
                        matchedRule = "blocked_command:$pat",
                        autoApproved = false
                    )
                }
            }
        }

        // Blocked path check
        request.filePath?.let { fp ->
            for (pat in profile.blockedPathPatterns) {
                if (Pattern.compile(pat, Pattern.CASE_INSENSITIVE).matcher(fp).find()) {
                    return EvaluationResult(
                        outcome = DecisionOutcome.PENDING,
                        reason = "Path matches restricted pattern '$pat'. Confirmation required.",
                        riskLevel = RiskLevel.HIGH,
                        matchedRule = "blocked_path:$pat",
                        autoApproved = false
                    )
                }
            }
        }

        // Category check
        if (!profile.autoApproveCategories.contains(request.category)) {
            return EvaluationResult(
                outcome = DecisionOutcome.PENDING,
                reason = "Category '${request.category.displayName}' is not configured for auto-approval in '${profile.name}' profile.",
                riskLevel = risk,
                matchedRule = "category_not_whitelisted",
                autoApproved = false
            )
        }

        // Allowed command check
        if (request.command != null && profile.allowedCommandRegexes.isNotEmpty()) {
            val cmd = request.command.trim()
            var matched: String? = null
            for (pat in profile.allowedCommandRegexes) {
                if (Pattern.compile(pat, Pattern.CASE_INSENSITIVE).matcher(cmd).matches()) {
                    matched = pat
                    break
                }
            }
            if (matched == null) {
                return EvaluationResult(
                    outcome = DecisionOutcome.PENDING,
                    reason = "Command '$cmd' is not in the allowed command whitelist.",
                    riskLevel = RiskLevel.MEDIUM,
                    matchedRule = "command_not_whitelisted",
                    autoApproved = false
                )
            }
        }

        return EvaluationResult(
            outcome = DecisionOutcome.APPROVED,
            reason = "Action safely evaluated and permitted by '${profile.name}' profile rules.",
            riskLevel = risk,
            matchedRule = "policy:${profile.name.lowercase()}",
            autoApproved = true
        )
    }
}
