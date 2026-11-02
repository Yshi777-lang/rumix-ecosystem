package com.rumix.core

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.rumix.R

object NotificationHelper {
    const val CHANNEL_SERVICE = "rumix_service"
    const val CHANNEL_CONSENT = "rumix_consent"
    const val NOTIF_SERVICE_ID = 1
    const val NOTIF_CONSENT_BASE = 1000

    fun createChannels(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            nm.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_SERVICE,
                    context.getString(R.string.notif_channel_service),
                    NotificationManager.IMPORTANCE_LOW
                )
            )
            nm.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_CONSENT,
                    context.getString(R.string.notif_channel_consent),
                    NotificationManager.IMPORTANCE_HIGH
                ).apply { enableVibration(true) }
            )
        }
    }

    fun serviceNotification(context: Context): android.app.Notification =
        NotificationCompat.Builder(context, CHANNEL_SERVICE)
            .setContentTitle(context.getString(R.string.notif_service_title))
            .setContentText(context.getString(R.string.notif_service_text))
            .setSmallIcon(android.R.drawable.ic_lock_power_off)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()

    fun consentNotification(context: Context, pending: ConsentManager.Pending): android.app.Notification {
        val approve = PendingIntent.getBroadcast(
            context,
            pending.id.hashCode() * 2 + 1,
            Intent(context, ConsentReceiver::class.java)
                .putExtra(ConsentReceiver.EXTRA_ID, pending.id)
                .putExtra(ConsentReceiver.EXTRA_APPROVE, true),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val deny = PendingIntent.getBroadcast(
            context,
            pending.id.hashCode() * 2 + 2,
            Intent(context, ConsentReceiver::class.java)
                .putExtra(ConsentReceiver.EXTRA_ID, pending.id)
                .putExtra(ConsentReceiver.EXTRA_APPROVE, false),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val openApp = PendingIntent.getActivity(
            context,
            pending.id.hashCode(),
            context.packageManager.getLaunchIntentForPackage(context.packageName),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(context, CHANNEL_CONSENT)
            .setContentTitle(pending.title)
            .setContentText(pending.detail)
            .setStyle(NotificationCompat.BigTextStyle().bigText(pending.detail + "\n\n" + (pending.riskNote ?: "")))
            .setSmallIcon(android.R.drawable.ic_lock_lock)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(openApp)
            .addAction(0, context.getString(R.string.notif_approve), approve)
            .addAction(0, context.getString(R.string.notif_deny), deny)
            .build()
    }
}
