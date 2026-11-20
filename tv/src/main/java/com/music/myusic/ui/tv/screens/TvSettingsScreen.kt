package com.music.myusic.ui.tv.screens

import android.widget.Toast
import androidx.appcompat.app.AppCompatDelegate
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.os.LocaleListCompat
import com.music.myusic.BuildConfig
import com.music.myusic.MyusicApplication
import com.music.myusic.R
import com.music.myusic.data.AppUpdateChecker
import com.music.myusic.data.LocaleTags
import com.music.myusic.data.settings.AppSettings
import com.music.myusic.data.settings.TvSettings
import com.music.myusic.ui.MainViewModel
import com.music.myusic.ui.components.SUPPORTED_LANGUAGES
import com.music.myusic.ui.components.languageDisplayNameRes
import com.music.myusic.ui.tv.TvAppMark
import com.music.myusic.ui.tv.audio.TvSpatialAudioEngine
import com.music.myusic.ui.tv.components.TvAboutDialog
import com.music.myusic.ui.tv.components.TvChromePinned
import com.music.myusic.ui.tv.components.TvDialog
import com.music.myusic.ui.tv.components.TvDialogButton
import com.music.myusic.ui.tv.components.TvListHeader
import com.music.myusic.ui.tv.components.TvListRow
import com.music.myusic.ui.tv.dialogs.TvEqualizerDialog
import com.music.myusic.ui.tv.dialogs.TvLyricsSourcesDialog
import com.music.myusic.ui.tv.dialogs.TvRefreshRateDialog
import com.music.myusic.ui.tv.dialogs.TvScrobbleDialog
import com.music.myusic.data.settings.TvPlayerStyle
import com.music.myusic.ui.tv.dialogs.TvThemeDialog
import com.music.myusic.ui.tv.dialogs.TvUpdateDialog
import com.music.myusic.ui.tv.display.TvRefreshRateController
import com.music.myusic.ui.tv.personalization.AppThemeOption
import com.music.myusic.ui.tv.theme.TvDimensions
import com.music.myusic.ui.tv.theme.TvGlass
import com.music.myusic.ui.tv.theme.TvType
import kotlinx.coroutines.launch

// Discord Rich Presence is hidden on TV for now; TvDiscordDialog is kept for when it returns.
private enum class SettingsSheet { Theme, RefreshRate, Equalizer, Scrobbling, LyricsSources, Language, Update, About }

private const val DefaultBlurb = "Playback, sound and display preferences for Myusic on this TV."

/**
 * Settings, as tvOS lays it out: the app on the left with a plain description of
 * whatever row has focus, the grouped rows on the right. Values are written out
 * ("On", "6 s") and change in place on select; rows that need a choice open one.
 */
@Composable
fun TvSettingsScreen(
    viewModel: MainViewModel,
    onOpenAccount: () -> Unit,
    onRunSetupAgain: () -> Unit,
    modifier: Modifier = Modifier,
) {
    TvChromePinned()
    val signedIn by viewModel.signedIn.collectAsState()
    val account by viewModel.account.collectAsState()

    val automix by AppSettings.smartFadeEnabled.collectAsState()
    val crossfade by AppSettings.crossfadeSeconds.collectAsState()
    val autoplay by AppSettings.autoplay.collectAsState()
    val skipSilence by AppSettings.skipSilence.collectAsState()
    val eqEnabled by AppSettings.equalizerEnabled.collectAsState()
    val spatial by TvSettings.spatialAudioEnabled.collectAsState()
    val loudness by AppSettings.loudnessNormalization.collectAsState()
    val usbDac by AppSettings.preferUsbDac.collectAsState()
    val syncedLyrics by AppSettings.syncedLyrics.collectAsState()
    val lyricsSources by AppSettings.lyricsSources.collectAsState()
    val canvas by AppSettings.animatedCanvas.collectAsState()
    val lyricsCanvas by TvSettings.tvLyricsCanvasEnabled.collectAsState()
    val nerdStats by AppSettings.showNerdStats.collectAsState()
    val themeId by TvSettings.tvTheme.collectAsState()
    val playerStyle by TvSettings.tvPlayerStyle.collectAsState()
    val uiScale by TvSettings.tvUiScale.collectAsState()
    val refreshRate by TvRefreshRateController.preference.collectAsState()
    val reduceMotion by AppSettings.reduceAnimation.collectAsState()
    val reduceTransparency by AppSettings.reduceDynamicBlur.collectAsState()

    var blurb by remember { mutableStateOf(DefaultBlurb) }
    var sheet by remember { mutableStateOf<SettingsSheet?>(null) }
    val update by AppUpdateChecker.available.collectAsState()
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var checkingUpdate by remember { mutableStateOf(false) }
    // Read on open; picking closes the dialog so this is a fresh read next time.
    val languageTitle = stringResource(R.string.app_language)
    val language = remember(sheet) {
        val picked = MyusicApplication.pickedAppLocale
            ?: AppCompatDelegate.getApplicationLocales().get(0)?.toLanguageTag()
            ?: LocaleTags.systemTag()
        languageDisplayNameRes(LocaleTags.appResourceTag(picked))
    }

    Row(
        modifier = modifier
            .fillMaxSize()
            .padding(top = TvDimensions.ContentTop),
    ) {
        Column(
            modifier = Modifier
                .weight(0.42f)
                .fillMaxHeight()
                .padding(horizontal = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            TvAppMark(size = 120.dp)
            Spacer(modifier = Modifier.height(22.dp))
            AnimatedContent(
                targetState = blurb,
                transitionSpec = { fadeIn().togetherWith(fadeOut()) },
                label = "settingsBlurb",
            ) { text ->
                Text(
                    text = text,
                    style = TvType.Callout,
                    color = TvGlass.TextSecondary,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.widthIn(max = 272.dp),
                )
            }
        }

        LazyColumn(
            modifier = Modifier
                .weight(0.58f)
                .fillMaxHeight(),
            contentPadding = PaddingValues(end = TvDimensions.SafeMarginHorizontal, bottom = 38.dp),
            verticalArrangement = Arrangement.spacedBy(5.dp),
        ) {
            item { TvListHeader("Account") }
            item {
                TvListRow(
                    title = "YouTube Music",
                    value = if (signedIn) account?.name ?: "Signed In" else "Sign In",
                    onFocused = { blurb = "Your library, playlists and recommendations come from this account." },
                    onClick = onOpenAccount,
                )
            }

            item { TvListHeader("Playback") }
            item {
                TvListRow(
                    title = "Automix",
                    value = onOff(automix),
                    onFocused = { blurb = "Blends one song into the next, matched to their tempo." },
                    onClick = { AppSettings.setSmartFadeEnabled(!automix) },
                )
            }
            item {
                TvListRow(
                    title = "Crossfade",
                    value = if (crossfade > 0) "$crossfade s" else "Off",
                    onFocused = { blurb = "Fades each song out as the next one fades in. Select to change the length." },
                    onClick = {
                        AppSettings.setCrossfadeSeconds(
                            when (crossfade) {
                                0 -> 3
                                3 -> 6
                                6 -> 10
                                else -> 0
                            },
                        )
                    },
                )
            }
            item {
                TvListRow(
                    title = "Autoplay",
                    value = onOff(autoplay),
                    onFocused = { blurb = "When the queue ends, keeps playing music similar to what you were listening to." },
                    onClick = { AppSettings.setAutoplay(!autoplay) },
                )
            }
            item {
                TvListRow(
                    title = "Skip Silence",
                    value = onOff(skipSilence),
                    onFocused = { blurb = "Skips over silent stretches at the start and end of songs." },
                    onClick = { AppSettings.setSkipSilence(!skipSilence) },
                )
            }

            item { TvListHeader("Sound") }
            item {
                TvListRow(
                    title = "Equalizer",
                    value = onOff(eqEnabled),
                    onFocused = { blurb = "Shape the sound with presets or seven bands of your own." },
                    onClick = { sheet = SettingsSheet.Equalizer },
                )
            }
            item {
                TvListRow(
                    title = "Spatial Audio",
                    value = onOff(spatial),
                    onFocused = { blurb = "Widens stereo music using the TV's audio virtualizer, where it has one." },
                    onClick = {
                        TvSettings.setSpatialAudioEnabled(!spatial)
                        TvSpatialAudioEngine.setEnabled(!spatial)
                    },
                )
            }
            item {
                TvListRow(
                    title = "Sound Check",
                    value = onOff(loudness),
                    onFocused = { blurb = "Plays every song at the same perceived loudness." },
                    onClick = { AppSettings.setLoudnessNormalization(!loudness) },
                )
            }
            item {
                TvListRow(
                    title = "USB DAC",
                    value = onOff(usbDac),
                    onFocused = { blurb = "Sends audio straight to a connected USB DAC, unchanged, when one is attached." },
                    onClick = { AppSettings.setPreferUsbDac(!usbDac) },
                )
            }

            item { TvListHeader("Now Playing") }
            item {
                TvListRow(
                    title = "Synced Lyrics",
                    value = onOff(syncedLyrics),
                    onFocused = { blurb = "Lyrics that follow along with the song, line by line." },
                    onClick = { AppSettings.setSyncedLyrics(!syncedLyrics) },
                )
            }
            item {
                TvListRow(
                    title = "Lyrics Sources",
                    value = "${lyricsSources.size} On",
                    onFocused = { blurb = "Choose which lyric databases to ask, and in what order." },
                    onClick = { sheet = SettingsSheet.LyricsSources },
                )
            }
            item {
                TvListRow(
                    title = "Motion Artwork",
                    value = onOff(canvas),
                    onFocused = { blurb = "Plays a song's looping video artwork behind the player, when it has one." },
                    onClick = { AppSettings.setAnimatedCanvas(!canvas) },
                )
            }
            item {
                TvListRow(
                    title = "Motion Artwork in Lyrics",
                    value = onOff(lyricsCanvas),
                    onFocused = { blurb = "Keeps the video artwork playing behind full-screen lyrics." },
                    onClick = { TvSettings.setTvLyricsCanvasEnabled(!lyricsCanvas) },
                )
            }
            item {
                TvListRow(
                    title = "Stats for Nerds",
                    value = onOff(nerdStats),
                    onFocused = { blurb = "Shows the codec, bitrate and sample rate of what's playing." },
                    onClick = { AppSettings.setShowNerdStats(!nerdStats) },
                )
            }

            item { TvListHeader("Display") }
            item {
                TvListRow(
                    title = "Appearance",
                    value = AppThemeOption.fromId(themeId).title,
                    onFocused = { blurb = "The background behind Myusic's pages." },
                    onClick = { sheet = SettingsSheet.Theme },
                )
            }
            item {
                TvListRow(
                    title = "Player Background",
                    value = playerStyle.label,
                    onFocused = { blurb = "What Now Playing shows behind the song: the artwork's colours, or AMOLED's pure black." },
                    onClick = {
                        val styles = TvPlayerStyle.entries
                        TvSettings.setTvPlayerStyle(styles[(playerStyle.ordinal + 1) % styles.size])
                    },
                )
            }
            item {
                TvListRow(
                    title = "Interface Size",
                    value = "${(uiScale * 100).toInt()}%",
                    onFocused = { blurb = "Makes everything larger or smaller. Select to step through sizes." },
                    onClick = {
                        val steps = listOf(0.8f, 0.9f, 1f, 1.1f, 1.2f, 1.3f)
                        val next = steps.firstOrNull { it > uiScale + 0.01f } ?: steps.first()
                        TvSettings.setTvUiScale(next)
                    },
                )
            }
            item {
                TvListRow(
                    title = "Refresh Rate",
                    value = refreshRate.label.substringBefore(" ("),
                    onFocused = { blurb = "How often the screen redraws while you browse." },
                    onClick = { sheet = SettingsSheet.RefreshRate },
                )
            }
            item {
                TvListRow(
                    title = "Reduce Motion",
                    value = onOff(reduceMotion),
                    onFocused = { blurb = "Calms the moving background and other decorative animation." },
                    onClick = { AppSettings.setReduceAnimation(!reduceMotion) },
                )
            }
            item {
                TvListRow(
                    title = "Reduce Transparency",
                    value = onOff(reduceTransparency),
                    onFocused = { blurb = "Replaces blurred backgrounds with solid ones. Helps on slower TVs." },
                    onClick = { AppSettings.setReduceDynamicBlur(!reduceTransparency) },
                )
            }

            item { TvListHeader("Connections") }
            item {
                TvListRow(
                    title = "Scrobbling",
                    onFocused = { blurb = "Last.fm and ListenBrainz." },
                    onClick = { sheet = SettingsSheet.Scrobbling },
                )
            }

            item { TvListHeader("General") }

            // The picker itself is the phone's; this row is the way back to
            // what it chose, since a TV cannot reach that screen.
            item {
                TvListRow(
                    title = languageTitle,
                    value = stringResource(language),
                    onFocused = { blurb = "Change the language of the app on this TV." },
                    onClick = { sheet = SettingsSheet.Language },
                )
            }
            item {
                val version = update?.version
                TvListRow(
                    title = "Software Update",
                    value = when {
                        checkingUpdate -> "Checking…"
                        version != null -> "$version Available"
                        else -> "Check for Updates"
                    },
                    onFocused = {
                        blurb = if (version != null) {
                            "Download and install the new version of Myusic for TV."
                        } else {
                            "Ask GitHub whether a newer version of Myusic for TV is out."
                        }
                    },
                    onClick = {
                        if (version != null) {
                            sheet = SettingsSheet.Update
                        } else {
                            scope.launch {
                                checkingUpdate = true
                                try {
                                    when (AppUpdateChecker.check(force = true)) {
                                        AppUpdateChecker.CheckResult.UpdateAvailable ->
                                            sheet = SettingsSheet.Update
                                        AppUpdateChecker.CheckResult.UpToDate ->
                                            Toast.makeText(context, R.string.up_to_date, Toast.LENGTH_SHORT).show()
                                        AppUpdateChecker.CheckResult.Failed ->
                                            Toast.makeText(context, R.string.update_check_failed, Toast.LENGTH_SHORT).show()
                                        AppUpdateChecker.CheckResult.Skipped -> Unit
                                    }
                                } finally {
                                    checkingUpdate = false
                                }
                            }
                        }
                    },
                )
            }
            item {
                TvListRow(
                    title = "Set Up Again",
                    onFocused = { blurb = "Go through the first-time setup again." },
                    onClick = onRunSetupAgain,
                )
            }
            item {
                TvListRow(
                    title = "About",
                    value = BuildConfig.VERSION_NAME,
                    onFocused = { blurb = DefaultBlurb },
                    onClick = { sheet = SettingsSheet.About },
                )
            }
        }
    }

    when (sheet) {
        SettingsSheet.Theme -> TvThemeDialog(onDismiss = { sheet = null })
        SettingsSheet.RefreshRate -> TvRefreshRateDialog(onDismiss = { sheet = null })
        SettingsSheet.Equalizer -> TvEqualizerDialog(onDismiss = { sheet = null })
        SettingsSheet.Scrobbling -> TvScrobbleDialog(onDismiss = { sheet = null })
        SettingsSheet.LyricsSources -> TvLyricsSourcesDialog(onDismiss = { sheet = null })
        SettingsSheet.Language -> TvLanguageDialog(onDismiss = { sheet = null })
        SettingsSheet.Update -> update?.let { TvUpdateDialog(update = it, onDismiss = { sheet = null }) }
        SettingsSheet.About -> TvAboutDialog(onDismiss = { sheet = null })
        null -> Unit
    }
}

private fun onOff(value: Boolean) = if (value) "On" else "Off"

/**
 * Picks the app's language on TV.
 *
 * The same list and the same two records as the phone's picker, since the TV
 * app cannot show that one: the choice is written back with
 * [MyusicApplication.persistAppLocale] and applied on the next start, and
 * `setApplicationLocales` here carries it the rest of the way - this dialog
 * is recreated onto its own new language, and Settings picks the new name up
 * when it is opened again.
 */
@Composable
private fun TvLanguageDialog(onDismiss: () -> Unit) {
    val current = LocaleTags.appResourceTag(
        MyusicApplication.pickedAppLocale
            ?: AppCompatDelegate.getApplicationLocales().get(0)?.toLanguageTag()
            ?: LocaleTags.systemTag(),
    )
    TvDialog(title = stringResource(R.string.app_language), onDismissRequest = onDismiss) {
        LazyColumn(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            items(SUPPORTED_LANGUAGES, key = { it.tag }) { language ->
                val selected = LocaleTags.appResourceTag(language.tag) == current
                TvListRow(
                    title = stringResource(language.nameRes),
                    value = if (selected) stringResource(R.string.selected) else "",
                    enabled = !selected,
                    onClick = {
                        AppCompatDelegate.setApplicationLocales(
                            LocaleListCompat.forLanguageTags(LocaleTags.appResourceTag(language.tag)),
                        )
                        MyusicApplication.persistAppLocale(language.tag)
                        onDismiss()
                    },
                )
            }
        }
        TvDialogButton(text = stringResource(R.string.cancel), onClick = onDismiss, initialFocus = true)
    }
}
