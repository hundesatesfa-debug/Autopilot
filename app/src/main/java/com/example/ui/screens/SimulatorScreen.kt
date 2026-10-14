package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Science
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ActionCategory
import com.example.model.ApprovalEvent
import com.example.ui.components.AgentChip
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SimulatorScreen(
    viewModel: AutoPilotViewModel,
    modifier: Modifier = Modifier
) {
    val state by viewModel.uiState.collectAsState()

    var selectedAgentId by remember { mutableStateOf("cursor") }
    var selectedCategory by remember { mutableStateOf(ActionCategory.TEST_RUN) }
    var commandInput by remember { mutableStateOf("npm test") }
    var filePathInput by remember { mutableStateOf("") }
    var lastEvaluatedEvent by remember { mutableStateOf<ApprovalEvent?>(null) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Science,
                        contentDescription = "Sandbox",
                        tint = AutoPilotCyan,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Interactive Action Simulator",
                        color = TextPrimary,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Test agent requests in real-time to observe the 6-step Universal Approval workflow.",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
        }

        // Preset Test Scenarios
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
                    Text(
                        text = "Quick Test Presets",
                        color = TextPrimary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        PresetButton("Safe Unit Test (npm test)") {
                            selectedAgentId = "claude_code"
                            selectedCategory = ActionCategory.TEST_RUN
                            commandInput = "npm test"
                            filePathInput = ""
                        }

                        PresetButton("In-Repo File Edit (src/main.ts)") {
                            selectedAgentId = "cursor"
                            selectedCategory = ActionCategory.FILE_EDIT
                            commandInput = ""
                            filePathInput = "src/main.ts"
                        }

                        PresetButton("Sensitive Secret (.env)") {
                            selectedAgentId = "cursor"
                            selectedCategory = ActionCategory.FILE_EDIT
                            commandInput = ""
                            filePathInput = ".env"
                        }

                        PresetButton("Path Traversal (../../etc/shadow)") {
                            selectedAgentId = "google_antigravity"
                            selectedCategory = ActionCategory.FILE_EDIT
                            commandInput = ""
                            filePathInput = "../../etc/shadow"
                        }

                        PresetButton("Critical Delete (rm -rf /)") {
                            selectedAgentId = "cursor"
                            selectedCategory = ActionCategory.FILE_DELETE
                            commandInput = "rm -rf /"
                            filePathInput = ""
                        }

                        PresetButton("Privilege Escalation (sudo service)") {
                            selectedAgentId = "claude_code"
                            selectedCategory = ActionCategory.ADMIN_PRIVILEGES
                            commandInput = "sudo systemctl restart nginx"
                            filePathInput = ""
                        }
                    }
                }
            }
        }

        // Request Builder Card
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
                    Text(
                        text = "Request Builder",
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // Agent selector
                    Text("1. Originating Coding Agent:", color = TextSecondary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        state.agents.forEach { agent ->
                            val isSel = agent.id == selectedAgentId
                            FilterChip(
                                selected = isSel,
                                onClick = { selectedAgentId = agent.id },
                                label = { Text(agent.name, fontSize = 11.sp) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = AutoPilotBlue,
                                    selectedLabelColor = Color.White,
                                    containerColor = ObsidianCard,
                                    labelColor = TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Category selector
                    Text("2. Action Category:", color = TextSecondary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(6.dp))
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        listOf(
                            ActionCategory.TEST_RUN,
                            ActionCategory.FILE_EDIT,
                            ActionCategory.BUILD_RUN,
                            ActionCategory.PACKAGE_INSTALL,
                            ActionCategory.NETWORK_ACCESS,
                            ActionCategory.FILE_DELETE,
                            ActionCategory.ADMIN_PRIVILEGES
                        ).forEach { cat ->
                            val isSel = cat == selectedCategory
                            FilterChip(
                                selected = isSel,
                                onClick = { selectedCategory = cat },
                                label = { Text(cat.displayName, fontSize = 10.sp) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = AutoPilotBlue,
                                    selectedLabelColor = Color.White,
                                    containerColor = ObsidianCard,
                                    labelColor = TextSecondary
                                )
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    // Command input
                    Text("3. Command (Optional):", color = TextSecondary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(4.dp))
                    OutlinedTextField(
                        value = commandInput,
                        onValueChange = { commandInput = it },
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("simulator_command_input"),
                        placeholder = { Text("e.g. npm test, pytest, rm -rf", color = TextMuted, fontSize = 12.sp) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = AutoPilotBlue,
                            unfocusedBorderColor = ObsidianBorder,
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary
                        ),
                        singleLine = true,
                        shape = RoundedCornerShape(8.dp)
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    // File path input
                    Text("4. Target File Path (Optional):", color = TextSecondary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    Spacer(modifier = Modifier.height(4.dp))
                    OutlinedTextField(
                        value = filePathInput,
                        onValueChange = { filePathInput = it },
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("simulator_filepath_input"),
                        placeholder = { Text("e.g. src/index.ts, .env, ../../etc/passwd", color = TextMuted, fontSize = 12.sp) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = AutoPilotBlue,
                            unfocusedBorderColor = ObsidianBorder,
                            focusedTextColor = TextPrimary,
                            unfocusedTextColor = TextPrimary
                        ),
                        singleLine = true,
                        shape = RoundedCornerShape(8.dp)
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Evaluate button
                    Button(
                        onClick = {
                            val ev = viewModel.processSimulatedRequest(
                                agentId = selectedAgentId,
                                category = selectedCategory,
                                command = commandInput.takeIf { it.isNotBlank() },
                                filePath = filePathInput.takeIf { it.isNotBlank() },
                                actionDescription = "Simulated ${selectedCategory.displayName}"
                            )
                            lastEvaluatedEvent = ev
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = AutoPilotBlue),
                        shape = RoundedCornerShape(8.dp),
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("evaluate_simulation_button")
                    ) {
                        Icon(imageVector = Icons.Default.PlayArrow, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Evaluate with AutoPilot Rules Engine", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        // Evaluation Result Card
        lastEvaluatedEvent?.let { ev ->
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = ObsidianCard),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .border(1.dp, AutoPilotCyan.copy(alpha = 0.5f), RoundedCornerShape(12.dp))
                            .padding(14.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "Evaluation Result",
                                color = TextPrimary,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp
                            )
                            OutcomeBadge(outcome = ev.evaluation.outcome)
                        }

                        Spacer(modifier = Modifier.height(10.dp))

                        StepItem("1. Agent Identified", "${ev.request.agentName} (${ev.request.agentId})")
                        StepItem("2. Action & Category", ev.request.category.displayName)
                        StepItem("3. Inherent Risk Level", ev.evaluation.riskLevel.name)
                        StepItem("4. Matched Policy Rule", ev.evaluation.matchedRule ?: "None")
                        StepItem("5. Decision Reason", ev.evaluation.reason)
                        StepItem("6. Audit Log Recorded", "Stored locally with API key redaction")
                    }
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(30.dp))
        }
    }
}

@Composable
private fun PresetButton(label: String, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(6.dp))
            .background(Color(0xFF0F172A))
            .border(1.dp, Color(0xFF1E293B), RoundedCornerShape(6.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 6.dp)
    ) {
        Text(
            text = label,
            color = AutoPilotCyan,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
private fun StepItem(stepTitle: String, detail: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 3.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = stepTitle, color = TextSecondary, fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        Text(text = detail, color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Bold)
    }
}
