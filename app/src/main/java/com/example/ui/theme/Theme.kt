package com.example.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = AutoPilotBlue,
    onPrimary = Color.White,
    primaryContainer = AutoPilotBlueDark,
    onPrimaryContainer = Color(0xFFDBEAFE),
    secondary = AutoPilotCyan,
    onSecondary = Color.Black,
    secondaryContainer = Color(0xFF0E7490),
    tertiary = AutoPilotEmerald,
    onTertiary = Color.White,
    error = AutoPilotRose,
    onError = Color.White,
    background = ObsidianBg,
    onBackground = TextPrimary,
    surface = ObsidianSurface,
    onSurface = TextPrimary,
    surfaceVariant = ObsidianCard,
    onSurfaceVariant = TextSecondary,
    outline = ObsidianBorder,
)

private val LightColorScheme = lightColorScheme(
    primary = AutoPilotBlue,
    onPrimary = Color.White,
    secondary = AutoPilotCyan,
    tertiary = AutoPilotEmerald,
    background = Color(0xFFF8FAFC),
    onBackground = Color(0xFF0F172A),
    surface = Color.White,
    onSurface = Color(0xFF0F172A),
    surfaceVariant = Color(0xFFF1F5F9),
    onSurfaceVariant = Color(0xFF475569),
    outline = Color(0xFFCBD5E1),
)

@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = true, // Default to sleek dark cybernetic theme for developer tool
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content,
    )
}
