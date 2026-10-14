package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ActionCategory
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
fun RulesEditorScreen(
    viewModel: AutoPilotViewModel,
    modifier: Modifier = Modifier
) {
    val state by viewModel.uiState.collectAsState()
    val activeProfile = state.activeProfile

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Column {
                Text(
                    text = "Permission Profile & Rules Studio",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Configure which action categories and command patterns are safely automated.",
                    color = TextSecondary,
                    fontSize = 12.sp
                )
            }
        }

        // Profile Selection Bar
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
                        text = "Active Profile Selection",
                        color = TextPrimary,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(10.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        state.profiles.forEach { prof ->
                            val isSelected = prof.name.equals(activeProfile.name, ignoreCase = true)
                            FilterChip(
                                selected = isSelected,
                                onClick = { viewModel.setProfile(prof.name) },
                                label = { Text(prof.name, fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = AutoPilotBlue,
                                    selectedLabelColor = Color.White,
                                    containerColor = ObsidianCard,
                                    labelColor = TextSecondary
                                ),
                                modifier = Modifier
                                    .weight(1f)
                                    .testTag("rules_profile_${prof.name.lowercase()}")
                            )
                        }
                    }
                }
            }
        }

        // Categories Matrix
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
                        text = "Action Category Automation Matrix",
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Categories permitted for auto-approval under '${activeProfile.name}'",
                        color = TextSecondary,
                        fontSize = 11.sp
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    ActionCategory.values().forEach { cat ->
                        if (cat != ActionCategory.UNKNOWN) {
                            val isAllowed = activeProfile.autoApproveCategories.contains(cat)
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column {
                                    Text(
                                        text = cat.displayName,
                                        color = TextPrimary,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                    Text(
                                        text = when (cat) {
                                            ActionCategory.FILE_CREATE -> "Creates new workspace files"
                                            ActionCategory.FILE_EDIT -> "Modifies existing source code"
                                            ActionCategory.TEST_RUN -> "Executes test runner commands"
                                            ActionCategory.BUILD_RUN -> "Executes compilation and linters"
                                            ActionCategory.PACKAGE_INSTALL -> "Installs packages from registry"
                                            ActionCategory.NETWORK_ACCESS -> "External HTTP/remote queries"
                                            ActionCategory.FILE_DELETE -> "Removes files or directories"
                                            ActionCategory.ADMIN_PRIVILEGES -> "sudo, runas, or privilege elevation"
                                            ActionCategory.SENSITIVE_OP -> "Accesses secrets or system settings"
                                            else -> ""
                                        },
                                        color = TextSecondary,
                                        fontSize = 10.sp
                                    )
                                }

                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(if (isAllowed) AutoPilotEmerald.copy(alpha = 0.2f) else AutoPilotAmber.copy(alpha = 0.15f))
                                        .padding(horizontal = 8.dp, vertical = 3.dp)
                                ) {
                                    Text(
                                        text = if (isAllowed) "AUTO-APPROVED" else "REQUIRES CONFIRMATION",
                                        color = if (isAllowed) AutoPilotEmerald else AutoPilotAmber,
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // Allowed Command Whitelist
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
                        text = "Allowed Command Regex Whitelist",
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    if (activeProfile.allowedCommandRegexes.isEmpty()) {
                        Text(
                            text = "No commands automatically whitelisted in '${activeProfile.name}' profile.",
                            color = TextMuted,
                            fontSize = 11.sp
                        )
                    } else {
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp)
                        ) {
                            activeProfile.allowedCommandRegexes.forEach { pat ->
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(6.dp))
                                        .background(Color(0xFF0F172A))
                                        .border(1.dp, Color(0xFF1E293B), RoundedCornerShape(6.dp))
                                        .padding(horizontal = 8.dp, vertical = 4.dp)
                                ) {
                                    Text(
                                        text = pat,
                                        color = Color(0xFFA7F3D0),
                                        fontFamily = FontFamily.Monospace,
                                        fontSize = 10.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // Blocked Command Blacklist
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
                        text = "Strictly Blocked Command Patterns",
                        color = AutoPilotRose,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "These commands trigger immediate DENIAL for safety:",
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        activeProfile.blockedCommandRegexes.take(5).forEach { pat ->
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(6.dp))
                                    .background(Color(0xFF1F1218))
                                    .border(1.dp, AutoPilotRose.copy(alpha = 0.3f), RoundedCornerShape(6.dp))
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    text = pat,
                                    color = Color(0xFFFCA5A5),
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 11.sp
                                )
                            }
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
