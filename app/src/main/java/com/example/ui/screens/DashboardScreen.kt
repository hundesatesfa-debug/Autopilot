package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Block
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.HourglassTop
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Science
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ActionCategory
import com.example.model.AutomationStatus
import com.example.model.DecisionOutcome
import com.example.model.RiskLevel
import com.example.ui.components.AgentChip
import com.example.ui.components.MetricCard
import com.example.ui.components.OutcomeBadge
import com.example.ui.components.RiskBadge
import com.example.ui.theme.AutoPilotAmber
import com.example.ui.theme.AutoPilotBlue
import com.example.ui.theme.AutoPilotCyan
import com.example.ui.theme.AutoPilotEmerald
import com.example.ui.theme.AutoPilotRose
import com.example.ui.theme.ObsidianBorder
import com.example.ui.theme.ObsidianCard
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.viewmodel.AutoPilotViewModel
import com.example.viewmodel.Screen

@Composable
fun DashboardScreen(
    viewModel: AutoPilotViewModel,
    modifier: Modifier = Modifier
) {
    val state by viewModel.uiState.collectAsState()

    val totalPending = state.pendingRequests.size
    val totalApproved = state.eventHistory.count {
        it.evaluation.outcome == DecisionOutcome.APPROVED || it.evaluation.outcome == DecisionOutcome.DRY_RUN_APPROVED
    }
    val totalBlocked = state.eventHistory.count {
        it.evaluation.outcome == DecisionOutcome.DENIED ||
                it.evaluation.outcome == DecisionOutcome.BLOCKED_EMERGENCY ||
                it.evaluation.outcome == DecisionOutcome.DRY_RUN_DENIED
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Top status card
        item {
            AutomationControlCard(
                status = state.automationStatus,
                isDryRun = state.isDryRun,
                onToggleStatus = { viewModel.toggleAutomation() },
                onToggleDryRun = { viewModel.toggleDryRun(it) },
                onOpenOnboarding = { viewModel.toggleOnboarding(true) }
            )
        }

        // Metrics Grid
        item {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    MetricCard(
                        title = "STATUS",
                        value = state.automationStatus.name,
                        accentColor = when (state.automationStatus) {
                            AutomationStatus.ACTIVE -> AutoPilotEmerald
                            AutomationStatus.PAUSED -> AutoPilotAmber
                            AutomationStatus.STOPPED -> TextSecondary
                            AutomationStatus.EMERGENCY_STOP -> AutoPilotRose
                        },
                        icon = when (state.automationStatus) {
                            AutomationStatus.ACTIVE -> Icons.Default.PlayArrow
                            AutomationStatus.PAUSED -> Icons.Default.Pause
                            AutomationStatus.STOPPED -> Icons.Default.Block
                            AutomationStatus.EMERGENCY_STOP -> Icons.Default.Warning
                        },
                        modifier = Modifier.weight(1f)
                    )
                    MetricCard(
                        title = "PENDING",
                        value = totalPending.toString(),
                        accentColor = AutoPilotAmber,
                        icon = Icons.Default.HourglassTop,
                        modifier = Modifier
                            .weight(1f)
                            .clickable { viewModel.navigateTo(Screen.PENDING) }
                    )
                }
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    MetricCard(
                        title = "AUTO-APPROVED",
                        value = totalApproved.toString(),
                        accentColor = AutoPilotCyan,
                        icon = Icons.Default.CheckCircle,
                        modifier = Modifier.weight(1f)
                    )
                    MetricCard(
                        title = "BLOCKED / HELD",
                        value = totalBlocked.toString(),
                        accentColor = AutoPilotRose,
                        icon = Icons.Default.Shield,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }

        // Permission Profile Selector
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = ObsidianCard),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .border(1.dp, ObsidianBorder, RoundedCornerShape(12.dp))
                        .padding(14.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Permission Profile",
                            color = TextPrimary,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                        Text(
                            text = "Configure rules",
                            color = AutoPilotBlue,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            modifier = Modifier.clickable { viewModel.navigateTo(Screen.RULES) }
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        state.profiles.forEach { profile ->
                            val isSelected = profile.name.equals(state.activeProfile.name, ignoreCase = true)
                            FilterChip(
                                selected = isSelected,
                                onClick = { viewModel.setProfile(profile.name) },
                                label = {
                                    Text(
                                        text = profile.name,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                                    )
                                },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = AutoPilotBlue,
                                    selectedLabelColor = Color.White,
                                    containerColor = ObsidianCard,
                                    labelColor = TextSecondary
                                ),
                                border = FilterChipDefaults.filterChipBorder(
                                    borderColor = if (isSelected) AutoPilotBlue else ObsidianBorder,
                                    selectedBorderColor = AutoPilotBlue,
                                    enabled = true,
                                    selected = isSelected
                                ),
                                modifier = Modifier
                                    .weight(1f)
                                    .testTag("profile_chip_${profile.name.lowercase()}")
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = state.activeProfile.description,
                        color = TextSecondary,
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )
                }
            }
        }

        // Detected Agents Health
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = ObsidianCard),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .border(1.dp, ObsidianBorder, RoundedCornerShape(12.dp))
                        .padding(14.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Connected Coding Agents",
                            color = TextPrimary,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                        Text(
                            text = "Diagnostics",
                            color = AutoPilotBlue,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            modifier = Modifier.clickable { viewModel.navigateTo(Screen.AGENTS) }
                        )
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        state.agents.forEach { agent ->
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(Color(0xFF0F172A))
                                    .padding(horizontal = 10.dp, vertical = 8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(
                                        modifier = Modifier
                                            .size(8.dp)
                                            .clip(CircleShape)
                                            .background(if (agent.running) AutoPilotEmerald else AutoPilotAmber)
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = agent.name,
                                        color = TextPrimary,
                                        fontWeight = FontWeight.SemiBold,
                                        fontSize = 13.sp
                                    )
                                }
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(4.dp))
                                        .background(AutoPilotBlue.copy(alpha = 0.15f))
                                        .padding(horizontal = 6.dp, vertical = 2.dp)
                                ) {
                                    Text(
                                        text = agent.integrationLevel.label,
                                        color = AutoPilotCyan,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // Quick Sandbox Simulation
        item {
            Card(
                colors = CardDefaults.cardColors(containerColor = ObsidianCard),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier
                        .border(1.dp, ObsidianBorder, RoundedCornerShape(12.dp))
                        .padding(14.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.Science,
                                contentDescription = "Sandbox",
                                tint = AutoPilotCyan,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "Action Simulation Sandbox",
                                color = TextPrimary,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp
                            )
                        }
                        Text(
                            text = "Full Studio",
                            color = AutoPilotBlue,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold,
                            modifier = Modifier.clickable { viewModel.navigateTo(Screen.SIMULATOR) }
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Test incoming agent commands against active policy rules:",
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                viewModel.processSimulatedRequest(
                                    agentId = "claude_code",
                                    category = ActionCategory.TEST_RUN,
                                    command = "npm test",
                                    actionDescription = "Simulate test suite execution"
                                )
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = AutoPilotEmerald.copy(alpha = 0.2f)),
                            border = ButtonDefaults.outlinedButtonBorder.copy(brush = androidx.compose.ui.graphics.SolidColor(AutoPilotEmerald)),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier
                                .weight(1f)
                                .testTag("sim_test_button")
                        ) {
                            Text("Safe: npm test", color = AutoPilotEmerald, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }

                        Button(
                            onClick = {
                                viewModel.processSimulatedRequest(
                                    agentId = "cursor",
                                    category = ActionCategory.FILE_DELETE,
                                    command = "rm -rf /",
                                    actionDescription = "Simulate dangerous recursive delete"
                                )
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = AutoPilotRose.copy(alpha = 0.2f)),
                            border = ButtonDefaults.outlinedButtonBorder.copy(brush = androidx.compose.ui.graphics.SolidColor(AutoPilotRose)),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier
                                .weight(1f)
                                .testTag("sim_danger_button")
                        ) {
                            Text("Danger: rm -rf", color = AutoPilotRose, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }

        // Recent Activity Feed
        item {
            Column {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Recent Activity Stream",
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                    Text(
                        text = "Full Audit Log (${state.eventHistory.size})",
                        color = AutoPilotBlue,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier.clickable { viewModel.navigateTo(Screen.HISTORY) }
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))

                if (state.eventHistory.isEmpty()) {
                    Text(
                        text = "No recent events.",
                        color = TextMuted,
                        fontSize = 12.sp,
                        modifier = Modifier.padding(vertical = 12.dp)
                    )
                } else {
                    state.eventHistory.take(5).forEach { ev ->
                        Card(
                            colors = CardDefaults.cardColors(containerColor = ObsidianCard),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp)
                        ) {
                            Row(
                                modifier = Modifier
                                    .border(1.dp, ObsidianBorder, RoundedCornerShape(8.dp))
                                    .padding(10.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                OutcomeBadge(outcome = ev.evaluation.outcome)
                                Spacer(modifier = Modifier.width(8.dp))
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = ev.request.actionDescription,
                                        color = TextPrimary,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        maxLines = 1
                                    )
                                    Text(
                                        text = "${ev.request.agentName} • ${ev.evaluation.reason}",
                                        color = TextSecondary,
                                        fontSize = 11.sp,
                                        maxLines = 1
                                    )
                                }
                                Spacer(modifier = Modifier.width(6.dp))
                                RiskBadge(risk = ev.evaluation.riskLevel)
                            }
                        }
                    }
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
fun AutomationControlCard(
    status: AutomationStatus,
    isDryRun: Boolean,
    onToggleStatus: () -> Unit,
    onToggleDryRun: (Boolean) -> Unit,
    onOpenOnboarding: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = ObsidianCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .border(1.dp, ObsidianBorder, RoundedCornerShape(12.dp))
                .padding(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(
                                when (status) {
                                    AutomationStatus.ACTIVE -> AutoPilotEmerald
                                    AutomationStatus.PAUSED -> AutoPilotAmber
                                    AutomationStatus.STOPPED -> TextSecondary
                                    AutomationStatus.EMERGENCY_STOP -> AutoPilotRose
                                }
                            )
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Automation: ${status.name}",
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    IconButton(onClick = onOpenOnboarding) {
                        Icon(
                            imageVector = Icons.Default.Info,
                            contentDescription = "Onboarding Guide",
                            tint = AutoPilotCyan
                        )
                    }

                    Button(
                        onClick = onToggleStatus,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = when (status) {
                                AutomationStatus.ACTIVE -> AutoPilotAmber.copy(alpha = 0.2f)
                                else -> AutoPilotEmerald.copy(alpha = 0.2f)
                            }
                        ),
                        border = ButtonDefaults.outlinedButtonBorder.copy(
                            brush = androidx.compose.ui.graphics.SolidColor(
                                if (status == AutomationStatus.ACTIVE) AutoPilotAmber else AutoPilotEmerald
                            )
                        ),
                        shape = RoundedCornerShape(6.dp),
                        modifier = Modifier.testTag("automation_toggle_button")
                    ) {
                        Text(
                            text = if (status == AutomationStatus.ACTIVE) "PAUSE" else "START",
                            color = if (status == AutomationStatus.ACTIVE) AutoPilotAmber else AutoPilotEmerald,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Dry-Run Mode toggle row
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    .background(Color(0xFF0F172A))
                    .padding(horizontal = 10.dp, vertical = 6.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Dry-Run Simulation Mode",
                        color = if (isDryRun) AutoPilotAmber else TextPrimary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Simulates decisions in audit logs without executing approvals",
                        color = TextSecondary,
                        fontSize = 10.sp
                    )
                }

                Switch(
                    checked = isDryRun,
                    onCheckedChange = onToggleDryRun,
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = AutoPilotAmber,
                        checkedTrackColor = AutoPilotAmber.copy(alpha = 0.4f),
                        uncheckedThumbColor = TextMuted,
                        uncheckedTrackColor = ObsidianBorder
                    ),
                    modifier = Modifier.testTag("dry_run_switch")
                )
            }
        }
    }
}
