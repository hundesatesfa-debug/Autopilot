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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DeleteSweep
import androidx.compose.material.icons.filled.Folder
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Terminal
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.DecisionOutcome
import com.example.ui.components.AgentChip
import com.example.ui.components.OutcomeBadge
import com.example.ui.components.RiskBadge
import com.example.ui.theme.AutoPilotBlue
import com.example.ui.theme.AutoPilotRose
import com.example.ui.theme.ObsidianBorder
import com.example.ui.theme.ObsidianCard
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.viewmodel.AutoPilotViewModel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun AuditLogScreen(
    viewModel: AutoPilotViewModel,
    modifier: Modifier = Modifier
) {
    val state by viewModel.uiState.collectAsState()
    val timeFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

    val filteredEvents = state.eventHistory.filter { ev ->
        val matchesQuery = state.searchQuery.isBlank() ||
                ev.request.actionDescription.contains(state.searchQuery, ignoreCase = true) ||
                (ev.request.command?.contains(state.searchQuery, ignoreCase = true) == true) ||
                (ev.request.filePath?.contains(state.searchQuery, ignoreCase = true) == true) ||
                ev.request.agentName.contains(state.searchQuery, ignoreCase = true)

        val matchesFilter = when (state.selectedFilterOutcome) {
            null -> true
            DecisionOutcome.APPROVED -> ev.evaluation.outcome == DecisionOutcome.APPROVED || ev.evaluation.outcome == DecisionOutcome.DRY_RUN_APPROVED
            DecisionOutcome.DENIED -> ev.evaluation.outcome == DecisionOutcome.DENIED || ev.evaluation.outcome == DecisionOutcome.DRY_RUN_DENIED
            DecisionOutcome.PENDING -> ev.evaluation.outcome == DecisionOutcome.PENDING
            DecisionOutcome.BLOCKED_EMERGENCY -> ev.evaluation.outcome == DecisionOutcome.BLOCKED_EMERGENCY
            else -> ev.evaluation.outcome == state.selectedFilterOutcome
        }
        matchesQuery && matchesFilter
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Audit & Decision History",
                        color = TextPrimary,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Local tamper-evident log (${state.eventHistory.size} total events)",
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                }

                TextButton(
                    onClick = { viewModel.clearHistory() },
                    modifier = Modifier.testTag("clear_history_button")
                ) {
                    Icon(
                        imageVector = Icons.Default.DeleteSweep,
                        contentDescription = "Clear",
                        tint = TextSecondary,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Clear", color = TextSecondary, fontSize = 12.sp)
                }
            }
        }

        // Search Bar
        item {
            OutlinedTextField(
                value = state.searchQuery,
                onValueChange = { viewModel.updateSearchQuery(it) },
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("audit_search_input"),
                placeholder = { Text("Search by command, path, agent...", color = TextMuted, fontSize = 12.sp) },
                leadingIcon = {
                    Icon(imageVector = Icons.Default.Search, contentDescription = "Search", tint = TextSecondary)
                },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = AutoPilotBlue,
                    unfocusedBorderColor = ObsidianBorder,
                    focusedContainerColor = ObsidianCard,
                    unfocusedContainerColor = ObsidianCard,
                    focusedTextColor = TextPrimary,
                    unfocusedTextColor = TextPrimary
                ),
                shape = RoundedCornerShape(10.dp)
            )
        }

        // Filter chips row
        item {
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                FilterChip(
                    selected = state.selectedFilterOutcome == null,
                    onClick = { viewModel.setFilterOutcome(null) },
                    label = { Text("All (${state.eventHistory.size})", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = AutoPilotBlue,
                        selectedLabelColor = Color.White,
                        containerColor = ObsidianCard,
                        labelColor = TextSecondary
                    )
                )

                FilterChip(
                    selected = state.selectedFilterOutcome == DecisionOutcome.APPROVED,
                    onClick = { viewModel.setFilterOutcome(DecisionOutcome.APPROVED) },
                    label = { Text("Approved", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = AutoPilotBlue,
                        selectedLabelColor = Color.White,
                        containerColor = ObsidianCard,
                        labelColor = TextSecondary
                    )
                )

                FilterChip(
                    selected = state.selectedFilterOutcome == DecisionOutcome.DENIED,
                    onClick = { viewModel.setFilterOutcome(DecisionOutcome.DENIED) },
                    label = { Text("Denied", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = AutoPilotBlue,
                        selectedLabelColor = Color.White,
                        containerColor = ObsidianCard,
                        labelColor = TextSecondary
                    )
                )

                FilterChip(
                    selected = state.selectedFilterOutcome == DecisionOutcome.PENDING,
                    onClick = { viewModel.setFilterOutcome(DecisionOutcome.PENDING) },
                    label = { Text("Pending", fontSize = 11.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        selectedContainerColor = AutoPilotBlue,
                        selectedLabelColor = Color.White,
                        containerColor = ObsidianCard,
                        labelColor = TextSecondary
                    )
                )
            }
        }

        // Event List
        if (filteredEvents.isEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 32.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text("No matching audit logs found.", color = TextMuted, fontSize = 12.sp)
                }
            }
        } else {
            items(filteredEvents, key = { it.eventId }) { ev ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = ObsidianCard),
                    shape = RoundedCornerShape(10.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .border(1.dp, ObsidianBorder, RoundedCornerShape(10.dp))
                            .padding(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    text = timeFormat.format(Date(ev.timestamp)),
                                    color = TextMuted,
                                    fontSize = 11.sp,
                                    fontFamily = FontFamily.Monospace
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                AgentChip(agentId = ev.request.agentId, agentName = ev.request.agentName)
                            }
                            OutcomeBadge(outcome = ev.evaluation.outcome)
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        Text(
                            text = ev.request.actionDescription,
                            color = TextPrimary,
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 13.sp
                        )

                        // Command / Path snippet
                        if (ev.request.command != null) {
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "$ ${ev.request.command}",
                                color = Color(0xFFA7F3D0),
                                fontFamily = FontFamily.Monospace,
                                fontSize = 11.sp,
                                maxLines = 2
                            )
                        } else if (ev.request.filePath != null) {
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "file: ${ev.request.filePath}",
                                color = Color(0xFF93C5FD),
                                fontFamily = FontFamily.Monospace,
                                fontSize = 11.sp,
                                maxLines = 1
                            )
                        }

                        Spacer(modifier = Modifier.height(6.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = ev.evaluation.reason,
                                color = TextSecondary,
                                fontSize = 11.sp,
                                modifier = Modifier.weight(1f)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            RiskBadge(risk = ev.evaluation.riskLevel)
                        }
                    }
                }
            }
        }

        item {
            Spacer(modifier = Modifier.height(30.dp))
        }
    }
}
