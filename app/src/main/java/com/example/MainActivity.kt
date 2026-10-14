package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Dangerous
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.HourglassTop
import androidx.compose.material.icons.filled.Hub
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Science
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Badge
import androidx.compose.material3.BadgedBox
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
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
import com.example.model.AutomationStatus
import com.example.ui.components.EmergencyStopButton
import com.example.ui.components.OnboardingDialog
import com.example.ui.screens.AgentsHealthScreen
import com.example.ui.screens.AuditLogScreen
import com.example.ui.screens.DashboardScreen
import com.example.ui.screens.PendingQueueScreen
import com.example.ui.screens.RulesEditorScreen
import com.example.ui.screens.SimulatorScreen
import com.example.ui.theme.AutoPilotAmber
import com.example.ui.theme.AutoPilotBlue
import com.example.ui.theme.AutoPilotCyan
import com.example.ui.theme.AutoPilotEmerald
import com.example.ui.theme.AutoPilotRose
import com.example.ui.theme.MyApplicationTheme
import com.example.ui.theme.ObsidianBg
import com.example.ui.theme.ObsidianBorder
import com.example.ui.theme.ObsidianCard
import com.example.ui.theme.ObsidianSurface
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary
import com.example.viewmodel.AutoPilotViewModel
import com.example.viewmodel.Screen

class MainActivity : ComponentActivity() {

    private val viewModel: AutoPilotViewModel by viewModels()

    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            MyApplicationTheme {
                val state by viewModel.uiState.collectAsState()

                // BackHandler returns to DASHBOARD if on a secondary screen
                if (state.currentScreen != Screen.DASHBOARD) {
                    BackHandler {
                        viewModel.navigateTo(Screen.DASHBOARD)
                    }
                }

                // Emergency Stop Alert Dialog
                if (state.showEmergencyDialog) {
                    AlertDialog(
                        onDismissRequest = { viewModel.dismissEmergencyDialog() },
                        title = {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    imageVector = Icons.Default.Dangerous,
                                    contentDescription = null,
                                    tint = AutoPilotRose,
                                    modifier = Modifier.size(24.dp)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = "EMERGENCY STOP ENGAGED",
                                    color = AutoPilotRose,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp
                                )
                            }
                        },
                        text = {
                            Text(
                                text = "AutoPilot AI has immediately locked all automated approvals.\n\n" +
                                        "No agent actions will be permitted until you reset the engine or switch to Manual review.",
                                color = TextPrimary,
                                fontSize = 13.sp,
                                lineHeight = 18.sp
                            )
                        },
                        confirmButton = {
                            Button(
                                onClick = { viewModel.dismissEmergencyDialog() },
                                colors = ButtonDefaults.buttonColors(containerColor = AutoPilotRose)
                            ) {
                                Text("Acknowledge", fontWeight = FontWeight.Bold)
                            }
                        },
                        containerColor = ObsidianSurface,
                        shape = RoundedCornerShape(14.dp)
                    )
                }

                // Onboarding Guide
                if (state.showOnboarding) {
                    OnboardingDialog(onDismiss = { viewModel.toggleOnboarding(false) })
                }

                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    containerColor = ObsidianBg,
                    topBar = {
                        TopAppBar(
                            title = {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(
                                        modifier = Modifier
                                            .size(28.dp)
                                            .clip(RoundedCornerShape(6.dp))
                                            .background(AutoPilotBlue.copy(alpha = 0.2f))
                                            .border(1.dp, AutoPilotCyan, RoundedCornerShape(6.dp)),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = "⚡",
                                            fontSize = 14.sp
                                        )
                                    }
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Column {
                                        Text(
                                            text = "AutoPilot AI",
                                            color = TextPrimary,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 16.sp
                                        )
                                        Text(
                                            text = "Coding Agent Automation",
                                            color = TextSecondary,
                                            fontSize = 10.sp
                                        )
                                    }
                                }
                            },
                            actions = {
                                if (state.isDryRun) {
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(4.dp))
                                            .background(AutoPilotAmber.copy(alpha = 0.2f))
                                            .border(1.dp, AutoPilotAmber, RoundedCornerShape(4.dp))
                                            .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text("DRY RUN", color = AutoPilotAmber, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                                    }
                                    Spacer(modifier = Modifier.width(8.dp))
                                }

                                EmergencyStopButton(
                                    onClick = { viewModel.triggerEmergencyStop() }
                                )
                            },
                            colors = TopAppBarDefaults.topAppBarColors(
                                containerColor = ObsidianSurface,
                                titleContentColor = TextPrimary
                            )
                        )
                    },
                    bottomBar = {
                        NavigationBar(
                            containerColor = ObsidianSurface,
                            tonalElevation = 8.dp
                        ) {
                            NavigationBarItem(
                                selected = state.currentScreen == Screen.DASHBOARD,
                                onClick = { viewModel.navigateTo(Screen.DASHBOARD) },
                                icon = { Icon(Icons.Default.Dashboard, contentDescription = "Dashboard") },
                                label = { Text("Home", fontSize = 10.sp) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = AutoPilotBlue,
                                    selectedTextColor = AutoPilotBlue,
                                    unselectedIconColor = TextMuted,
                                    unselectedTextColor = TextMuted,
                                    indicatorColor = AutoPilotBlue.copy(alpha = 0.15f)
                                )
                            )

                            NavigationBarItem(
                                selected = state.currentScreen == Screen.PENDING,
                                onClick = { viewModel.navigateTo(Screen.PENDING) },
                                icon = {
                                    BadgedBox(
                                        badge = {
                                            if (state.pendingRequests.isNotEmpty()) {
                                                Badge(containerColor = AutoPilotAmber) {
                                                    Text(state.pendingRequests.size.toString(), color = Color.Black, fontWeight = FontWeight.Bold)
                                                }
                                            }
                                        }
                                    ) {
                                        Icon(Icons.Default.HourglassTop, contentDescription = "Pending")
                                    }
                                },
                                label = { Text("Pending", fontSize = 10.sp) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = AutoPilotAmber,
                                    selectedTextColor = AutoPilotAmber,
                                    unselectedIconColor = TextMuted,
                                    unselectedTextColor = TextMuted,
                                    indicatorColor = AutoPilotAmber.copy(alpha = 0.15f)
                                )
                            )

                            NavigationBarItem(
                                selected = state.currentScreen == Screen.RULES,
                                onClick = { viewModel.navigateTo(Screen.RULES) },
                                icon = { Icon(Icons.Default.Tune, contentDescription = "Rules") },
                                label = { Text("Rules", fontSize = 10.sp) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = AutoPilotCyan,
                                    selectedTextColor = AutoPilotCyan,
                                    unselectedIconColor = TextMuted,
                                    unselectedTextColor = TextMuted,
                                    indicatorColor = AutoPilotCyan.copy(alpha = 0.15f)
                                )
                            )

                            NavigationBarItem(
                                selected = state.currentScreen == Screen.HISTORY,
                                onClick = { viewModel.navigateTo(Screen.HISTORY) },
                                icon = { Icon(Icons.Default.History, contentDescription = "Audit Log") },
                                label = { Text("Logs", fontSize = 10.sp) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = AutoPilotEmerald,
                                    selectedTextColor = AutoPilotEmerald,
                                    unselectedIconColor = TextMuted,
                                    unselectedTextColor = TextMuted,
                                    indicatorColor = AutoPilotEmerald.copy(alpha = 0.15f)
                                )
                            )

                            NavigationBarItem(
                                selected = state.currentScreen == Screen.AGENTS,
                                onClick = { viewModel.navigateTo(Screen.AGENTS) },
                                icon = { Icon(Icons.Default.Hub, contentDescription = "Agents") },
                                label = { Text("Agents", fontSize = 10.sp) },
                                colors = NavigationBarItemDefaults.colors(
                                    selectedIconColor = AutoPilotBlue,
                                    selectedTextColor = AutoPilotBlue,
                                    unselectedIconColor = TextMuted,
                                    unselectedTextColor = TextMuted,
                                    indicatorColor = AutoPilotBlue.copy(alpha = 0.15f)
                                )
                            )
                        }
                    }
                ) { innerPadding ->
                    Box(modifier = Modifier.padding(innerPadding)) {
                        when (state.currentScreen) {
                            Screen.DASHBOARD -> DashboardScreen(viewModel = viewModel)
                            Screen.PENDING -> PendingQueueScreen(viewModel = viewModel)
                            Screen.RULES -> RulesEditorScreen(viewModel = viewModel)
                            Screen.HISTORY -> AuditLogScreen(viewModel = viewModel)
                            Screen.AGENTS -> AgentsHealthScreen(viewModel = viewModel)
                            Screen.SIMULATOR -> SimulatorScreen(viewModel = viewModel)
                        }
                    }
                }
            }
        }
    }
}
