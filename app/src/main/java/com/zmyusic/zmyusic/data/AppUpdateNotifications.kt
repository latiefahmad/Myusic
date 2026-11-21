package com.zmyusic.zmyusic.data

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationCompat
import com.zmyusic.zmyusic.MainActivity
import com.zmyusic.zmyusic.R
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * The shade presence for an app update: one row saying a newer ZMyusic exists,
 * tapping which opens the update dialog.
 *
 * A plain notification rather than a foreground service — [AppUpdateChecker]
 * does its work in a coroutine and there is nothing to keep alive. It is only
 * ever posted *once per version* (the checker remembers what it announced), so
 * a resuming app does not re-notify for an update the user is already looking at.
 *
 * Every post is caught: without the notification permission the shade simply
 * never shows, and that must not fail the check.
 */
object AppUpdateNotifications {

    /** Set on the notification's tap target. Nothing else sets it. */
    const val EXTRA_SHOW_UPDATE = "zmyusic.showUpdate"

    private const val CHANNEL_ID = "app_updates"

    /** Distinct from the download, upload and sync channels' ids. */
    private const val NOTIFICATION_ID = 0x8177

    /**
     * Announces [info] in the shade. The tap target is [MainActivity] carrying
     * [EXTRA_SHOW_UPDATE], which the composition reads to pop the update dialog
     * it would otherwise only show on its own once-per-launch schedule.
     */
    fun post(context: Context, info: AppUpdateChecker.UpdateInfo) {
        runCatching {
            val manager = context.getSystemService(NotificationManager::class.java) ?: return
            manager.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_ID,
                    context.getString(R.string.software_update),
                    NotificationManager.IMPORTANCE_DEFAULT,
                ).apply {
                    description = context.getString(R.string.update_available_body, info.version)
                    setShowBadge(true)
                },
            )
            manager.notify(NOTIFICATION_ID, build(context, info))
        }
    }

    private val _pending = MutableStateFlow(false)

    /** Whether a tap has asked for the update dialog. Cleared by [handled]. */
    val pending: StateFlow<Boolean> = _pending.asStateFlow()

    /**
     * Reads an incoming intent, and reports whether it asked for the update
     * dialog. Mirrors [com.zmyusic.zmyusic.playback.PlayerDeepLink.consume]: the
     * activity is `singleTask`, so the extra arrives through `onCreate` on a cold
     * launch and `onNewIntent` every other time, and the composition watches this
     * for both.
     */
    fun consume(intent: Intent?): Boolean {
        if (intent == null || !intent.getBooleanExtra(EXTRA_SHOW_UPDATE, false)) return false
        // Cleared off the intent too: a singleTask activity keeps its launching
        // intent, so a leftover extra would re-open the dialog on every
        // configuration change.
        intent.removeExtra(EXTRA_SHOW_UPDATE)
        _pending.value = true
        return true
    }

    /** Called once the dialog has been put on screen. See [PlayerDeepLink.handled]. */
    fun handled() {
        _pending.value = false
    }

    /** Drops the announcement once its update has been acted on or is gone. */
    fun cancel(context: Context) {
        runCatching {
            context.getSystemService(NotificationManager::class.java)?.cancel(NOTIFICATION_ID)
        }
    }

    private fun build(context: Context, info: AppUpdateChecker.UpdateInfo) =
        NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification_logo)
            .setContentTitle(context.getString(R.string.update_available, info.version))
            .setContentText(context.getString(R.string.update_available_body, info.version))
            .setStyle(
                NotificationCompat.BigTextStyle()
                    .bigText(context.getString(R.string.update_available_body, info.version)),
            )
            .setContentIntent(openDialog(context))
            .setAutoCancel(true)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setCategory(NotificationCompat.CATEGORY_RECOMMENDATION)
            .build()

    /**
     * `SINGLE_TOP` so a tap while the app is already open delivers through
     * [MainActivity.onNewIntent][android.app.Activity.onNewIntent] rather than
     * stacking a second task on top of the one the user left.
     */
    private fun openDialog(context: Context): PendingIntent {
        val intent = Intent(context, MainActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            .putExtra(EXTRA_SHOW_UPDATE, true)
        return PendingIntent.getActivity(
            context,
            NOTIFICATION_ID,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }
}
