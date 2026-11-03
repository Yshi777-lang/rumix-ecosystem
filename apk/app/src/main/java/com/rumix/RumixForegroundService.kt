package com.rumix

import android.app.Service
import android.content.Intent
import android.os.IBinder
import com.rumix.core.NotificationHelper

class RumixForegroundService : Service() {

    override fun onCreate() {
        super.onCreate()
        NotificationHelper.createChannels(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NotificationHelper.NOTIF_SERVICE_ID, NotificationHelper.serviceNotification(this))
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
