// RumixForegroundService.kt — фоновый сервис для Shell
// Создано: 18.10.2026 (Тиамат + Зая)

package com.rumix

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

class RumixForegroundService : Service() {
    private var process: Process? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(1, notification)

        // Запускаем Flask в фоне
        try {
            val python = ProcessBuilder("python3", "app.py")
                .directory(java.io.File("/data/data/com.rumix/files/home/rumix/backend"))
                .redirectErrorStream(true)
                .start()
            process = python
        } catch (e: Exception) {
            e.printStackTrace()
        }

        return START_STICKY
    }

    override fun onDestroy() {
        process?.destroy()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "rumix_service",
                "Rumix Shell",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, "rumix_service")
            .setContentTitle("Rumix Shell")
            .setContentText("Дом работает в фоне")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()
    }
}
