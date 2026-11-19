package com.music.myusic.desktop

/** Which desktop this is running on. */
internal object DesktopPlatform {

    private val name: String = System.getProperty("os.name").orEmpty()

    val isWindows: Boolean = name.startsWith("Windows", ignoreCase = true)

    val isLinux: Boolean = name.contains("linux", ignoreCase = true)

    val isMac: Boolean = name.contains("mac", ignoreCase = true)

    /** The same machine name Discord's client reports, for Rich Presence. */
    val discordOs: String = when {
        isWindows -> "Windows"
        isMac -> "macOS"
        else -> "Linux"
    }

    /** Whether the application draws the window's own frame instead of the system drawing it. */
    val drawsOwnWindowFrame: Boolean = isWindows
}
