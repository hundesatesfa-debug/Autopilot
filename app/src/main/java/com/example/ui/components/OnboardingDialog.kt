package com.example.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Dangerous
import androidx.compose.material.icons.filled.Security
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.AutoPilotBlue
import com.example.ui.theme.AutoPilotCyan
import com.example.ui.theme.AutoPilotEmerald
import com.example.ui.theme.AutoPilotRose
import com.example.ui.theme.ObsidianBorder
import com.example.ui.theme.ObsidianCard
import com.example.ui.theme.ObsidianSurface
import com.example.ui.theme.TextMuted
import com.example.ui.theme.TextPrimary
import com.example.ui.theme.TextSecondary

@Composable
fun OnboardingDialog(
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            Button(
                onClick = onDismiss,
                colors = ButtonDefaults.buttonColors(containerColor = AutoPilotBlue),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.testTag("onboarding_dismiss_button")
            ) {
                Text("Got It, Let's Build!", fontWeight = FontWeight.Bold)
            }
        },
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Security,
                    contentDescription = "Shield",
                    tint = AutoPilotCyan,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Welcome to AutoPilot AI",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        },
        text = {
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .fillMaxWidth()
            ) {
                Text(
                    text = "AutoPilot AI eliminates repetitive permission interruptions when working with AI coding agents, without compromising security.",
                    color = TextSecondary,
                    fontSize = 13.sp,
                    lineHeight = 18.sp
                )

                Spacer(modifier = Modifier.height(14.dp))

                ConceptItem(
                    icon = Icons.Default.Tune,
                    iconColor = AutoPilotCyan,
                    title = "Native Integration vs Visual Automation",
                    description = "We prioritize official settings (.cursorrules, ~/.claude.json) and agent IPC over visual automation. We never approve arbitrary dialogs just because they say 'Allow'."
                )

                Spacer(modifier = Modifier.height(10.dp))

                ConceptItem(
                    icon = Icons.Default.Security,
                    iconColor = AutoPilotEmerald,
                    title = "Strict Workspace Sandboxing",
                    description = "All file operations are contained to your workspace root. Path traversal (../) and touches to .env or system files require explicit manual confirmation."
                )

                Spacer(modifier = Modifier.height(10.dp))

                ConceptItem(
                    icon = Icons.Default.CheckCircle,
                    iconColor = AutoPilotBlue,
                    title = "Balanced Profile (Default)",
                    description = "Safely auto-approves safe tests, builds, and in-repo edits. Strictly holds deletions, package installations, and network access for your review."
                )

                Spacer(modifier = Modifier.height(10.dp))

                ConceptItem(
                    icon = Icons.Default.Dangerous,
                    iconColor = AutoPilotRose,
                    title = "Immediate Emergency Stop",
                    description = "One click immediately freezes all background automation and locks the engine in a fail-safe state."
                )
            }
        },
        containerColor = ObsidianSurface,
        shape = RoundedCornerShape(16.dp),
        modifier = modifier
    )
}

@Composable
private fun ConceptItem(
    icon: ImageVector,
    iconColor: Color,
    title: String,
    description: String
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(ObsidianCard)
            .border(1.dp, ObsidianBorder, RoundedCornerShape(10.dp))
            .padding(10.dp)
    ) {
        Row {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = iconColor,
                modifier = Modifier
                    .size(20.dp)
                    .padding(top = 2.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column {
                Text(
                    text = title,
                    color = TextPrimary,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = description,
                    color = TextSecondary,
                    fontSize = 11.sp,
                    lineHeight = 15.sp
                )
            }
        }
    }
}
