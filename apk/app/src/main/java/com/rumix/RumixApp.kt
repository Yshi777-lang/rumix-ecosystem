package com.rumix

import android.app.Application
import com.rumix.core.EvidenceJournal
import com.rumix.core.NotificationHelper
import com.rumix.net.RumixClient
import com.rumix.tools.BuiltinChatToolAccess
import com.rumix.tools.ToolRegistry
import java.io.File

class RumixApp : Application() {

    lateinit var journal: EvidenceJournal
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this

        NotificationHelper.createChannels(this)
        journal = EvidenceJournal(File(filesDir, "evidence.jsonl"))

        val prefs = getSharedPreferences("rumix", MODE_PRIVATE)
        RumixClient.host = prefs.getString("backend_host", RumixClient.DEFAULT_HOST) ?: RumixClient.DEFAULT_HOST
        RumixClient.port = prefs.getInt("backend_port", RumixClient.DEFAULT_PORT)
        RumixClient.token = prefs.getString("backend_token", "") ?: ""

        try {
            ToolRegistry.loadFromServiceLoader(classLoader)
        } catch (_: Throwable) {
        }
        if (ToolRegistry.all.isEmpty()) {
            BuiltinChatToolAccess.registerDefaults()
        }

        journal.record(
            source = "rumix-core",
            test = "boot",
            result = "старт, инструментов: ${ToolRegistry.all.size}, бэкенд: ${RumixClient.baseUrl}",
            confidence = "high",
        )
    }

    fun saveBackend(host: String, port: Int, token: String = RumixClient.token) {
        RumixClient.host = host
        RumixClient.port = port
        RumixClient.token = token.trim()
        getSharedPreferences("rumix", MODE_PRIVATE).edit()
            .putString("backend_host", host)
            .putInt("backend_port", port)
            .putString("backend_token", RumixClient.token)
            .apply()
    }

    companion object {
        lateinit var instance: RumixApp
            private set
    }
}
