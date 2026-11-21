package com.zmyusic.zmyusic.ui.tv.personalization

import androidx.compose.runtime.Immutable
import androidx.compose.ui.graphics.Color

enum class AppThemeOption(
    val id: String,
    val title: String,
    val description: String,
) {
    DYNAMIC_ARTWORK(
        id = "dynamic_artwork",
        title = "Artwork",
        description = "Dark, softly tinted by the artwork of what's playing.",
    ),
    MIDNIGHT(
        id = "midnight",
        title = "Midnight",
        description = "A deep navy background.",
    ),
    PURE_BLACK(
        id = "pure_black",
        title = "Pure Black",
        description = "True black, for OLED screens.",
    );

    companion object {
        fun fromId(id: String?): AppThemeOption = when (id?.lowercase()) {
            "midnight" -> MIDNIGHT
            "pure_black", "oled" -> PURE_BLACK
            else -> DYNAMIC_ARTWORK
        }
    }
}

@Immutable
data class TvThemePalette(
    val background: Color,
    val backgroundElevated: Color,
    val surface: Color,
    val surfaceVariant: Color,
    val surfaceFocused: Color,
    val surfaceSelected: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val textMuted: Color,
    val accent: Color,
    val accentGlow: Color,
    val borderFocused: Color,
)

fun AppThemeOption.getPalette(): TvThemePalette = when (this) {
    AppThemeOption.DYNAMIC_ARTWORK -> TvThemePalette(
        background = Color(0xFF08080B),
        backgroundElevated = Color(0xFF101015),
        surface = Color(0xFF17171E),
        surfaceVariant = Color(0xFF22222C),
        surfaceFocused = Color(0xFF323242),
        surfaceSelected = Color(0xFF38151D),
        textPrimary = Color(0xFFFFFFFF),
        textSecondary = Color(0xFFA0A0AB),
        textMuted = Color(0xFF6E6E7A),
        accent = Color(0xFFFFFFFF),
        accentGlow = Color(0x66FFFFFF),
        borderFocused = Color(0xFFFFFFFF),
    )
    AppThemeOption.MIDNIGHT -> TvThemePalette(
        background = Color(0xFF0A0E17),
        backgroundElevated = Color(0xFF111827),
        surface = Color(0xFF1E293B),
        surfaceVariant = Color(0xFF334155),
        surfaceFocused = Color(0xFF475569),
        surfaceSelected = Color(0xFF1E1B4B),
        textPrimary = Color(0xFFF8FAFC),
        textSecondary = Color(0xFF94A3B8),
        textMuted = Color(0xFF64748B),
        accent = Color(0xFF7C5CFC),
        accentGlow = Color(0x667C5CFC),
        borderFocused = Color(0xFF818CF8),
    )
    AppThemeOption.PURE_BLACK -> TvThemePalette(
        background = Color(0xFF000000),
        backgroundElevated = Color(0xFF080808),
        surface = Color(0xFF121212),
        surfaceVariant = Color(0xFF1E1E1E),
        surfaceFocused = Color(0xFF2C2C2C),
        surfaceSelected = Color(0xFF202020),
        textPrimary = Color(0xFFFFFFFF),
        textSecondary = Color(0xFFB0B0B0),
        textMuted = Color(0xFF707070),
        accent = Color(0xFFFFFFFF),
        accentGlow = Color(0x66FFFFFF),
        borderFocused = Color(0xFFFFFFFF),
    )
}
