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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Dangerous
import androidx.compose.material.icons.filled.HourglassTop
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
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
import com.example.model.DecisionOutcome
import com.example.model.RiskLevel
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

@Composable
fun RiskBadge(risk: RiskLevel, modifier: Modifier = Modifier) {
    val (bgColor, textColor, label) = when (risk) {
        RiskLevel.SAFE -> Triple(AutoPilotEmerald.copy(alpha = 0.2f), AutoPilotEmerald, "SAFE")
        RiskLevel.LOW -> Triple(AutoPilotCyan.copy(alpha = 0.2f), AutoPilotCyan, "LOW")
        RiskLevel.MEDIUM -> Triple(AutoPilotAmber.copy(alpha = 0.2f), AutoPilotAmber, "MEDIUM")
        RiskLevel.HIGH -> Triple(AutoPilotRose.copy(alpha = 0.25f), AutoPilotRose, "HIGH RISK")
        RiskLevel.CRITICAL -> Triple(Color(0xFF991B1B), Color(0xFFFCA5A5), "CRITICAL")
    }

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(6.dp))
            .background(bgColor)
            .border(1.dp, textColor.copy(alpha = 0.5f), RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = label,
            color = textColor,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun OutcomeBadge(outcome: DecisionOutcome, modifier: Modifier = Modifier) {
    val (bgColor, textColor, label) = when (outcome) {
        DecisionOutcome.APPROVED -> Triple(AutoPilotEmerald.copy(alpha = 0.2f), AutoPilotEmerald, "APPROVED")
        DecisionOutcome.DENIED -> Triple(AutoPilotRose.copy(alpha = 0.2f), AutoPilotRose, "DENIED")
        DecisionOutcome.PENDING -> Triple(AutoPilotAmber.copy(alpha = 0.2f), AutoPilotAmber, "PENDING")
        DecisionOutcome.BLOCKED_EMERGENCY -> Triple(Color(0xFF7F1D1D), Color(0xFFFECACA), "EMERGENCY BLOCKED")
        DecisionOutcome.DRY_RUN_APPROVED -> Triple(AutoPilotBlue.copy(alpha = 0.2f), AutoPilotBlue, "DRY-RUN (ALLOW)")
        DecisionOutcome.DRY_RUN_DENIED -> Triple(Color(0xFF581C87), Color(0xFFE9D5FF), "DRY-RUN (DENY)")
    }

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(6.dp))
            .background(bgColor)
            .border(1.dp, textColor.copy(alpha = 0.4f), RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = label,
            color = textColor,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun AgentChip(agentId: String, agentName: String, modifier: Modifier = Modifier) {
    val (dotColor, borderColor) = when (agentId) {
        "cursor" -> AutoPilotCyan to AutoPilotCyan.copy(alpha = 0.4f)
        "claude_code" -> AutoPilotAmber to AutoPilotAmber.copy(alpha = 0.4f)
        "google_antigravity" -> AutoPilotBlue to AutoPilotBlue.copy(alpha = 0.4f)
        "vscode_copilot" -> AutoPilotEmerald to AutoPilotEmerald.copy(alpha = 0.4f)
        else -> TextSecondary to ObsidianBorder
    }

    Row(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(ObsidianCard)
            .border(1.dp, borderColor, RoundedCornerShape(8.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .clip(CircleShape)
                .background(dotColor)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = agentName,
            color = TextPrimary,
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    accentColor: Color,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = ObsidianCard),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .border(1.dp, ObsidianBorder, RoundedCornerShape(12.dp))
                .padding(14.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = title,
                    tint = accentColor,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = title,
                    color = TextSecondary,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                color = accentColor,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun EmergencyStopButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier
            .testTag("emergency_stop_button"),
        colors = ButtonDefaults.buttonColors(
            containerColor = AutoPilotRose,
            contentColor = Color.White
        ),
        shape = RoundedCornerShape(8.dp)
    ) {
        Icon(
            imageVector = Icons.Default.Dangerous,
            contentDescription = "Emergency Stop",
            modifier = Modifier.size(18.dp)
        )
        Spacer(modifier = Modifier.width(6.dp))
        Text(
            text = "EMERGENCY STOP",
            fontWeight = FontWeight.Bold,
            fontSize = 12.sp
        )
    }
}
