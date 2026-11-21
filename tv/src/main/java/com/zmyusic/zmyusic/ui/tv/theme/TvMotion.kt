package com.zmyusic.zmyusic.ui.tv.theme

import androidx.compose.animation.core.SpringSpec
import androidx.compose.animation.core.spring

enum class AppleSpringPreset(val stiffness: Float, val dampingRatio: Float) {
    /** Snappy response for buttons, cards, D-pad focus state transitions (400f, 0.65f) */
    Snappy(400f, 0.65f),
    /** Smooth fluid motion for tabs, navigation pills, progress bars (200f, 0.75f) */
    Smooth(200f, 0.75f),
    /** Gentle motion for screen transitions, lyrics scale, backdrop shifts (120f, 0.85f) */
    Gentle(120f, 0.85f),
}

/**
 * Creates an Apple-spec spring animation spec.
 */
fun <T> appleSpring(
    preset: AppleSpringPreset = AppleSpringPreset.Smooth,
    visibilityThreshold: T? = null,
): SpringSpec<T> = spring(
    dampingRatio = preset.dampingRatio,
    stiffness = preset.stiffness,
    visibilityThreshold = visibilityThreshold,
)
