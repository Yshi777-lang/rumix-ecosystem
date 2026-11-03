package com.rumix.core

import android.content.Context
import com.rumix.RumixApp
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withTimeoutOrNull
import java.util.UUID

object ConsentManager {

    data class Pending(
        val id: String,
        val title: String,
        val detail: String,
        val level: GateLevel,
        val riskNote: String?,
        val createdAt: Long = System.currentTimeMillis(),
    )

    const val TIMEOUT_MS = 60_000L

    private val _pending = MutableStateFlow<List<Pending>>(emptyList())
    val pending: StateFlow<List<Pending>> = _pending

    private val deferreds = HashMap<String, CompletableDeferred<Boolean>>()
    private val lock = Any()

    fun ask(context: Context, title: String, detail: String, level: GateLevel, riskNote: String? = null): PendingConsent {
        val id = UUID.randomUUID().toString().substring(0, 8)
        val p = Pending(id, title, detail, level, riskNote)
        val d = CompletableDeferred<Boolean>()
        synchronized(lock) {
            deferreds[id] = d
            _pending.value = _pending.value + p
        }
        try {
            val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
            nm.notify(NotificationHelper.NOTIF_CONSENT_BASE + id.hashCode().and(0xffff),
                NotificationHelper.consentNotification(context, p))
        } catch (_: SecurityException) {
        }
        return PendingConsent(id, d, context.applicationContext)
    }

    fun resolve(id: String, approved: Boolean): Boolean {
        val d = synchronized(lock) {
            val dd = deferreds.remove(id) ?: return false
            _pending.value = _pending.value.filterNot { it.id == id }
            dd
        }
        try {
            val ctx = RumixApp.instance
            val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
            nm.cancel(NotificationHelper.NOTIF_CONSENT_BASE + id.hashCode().and(0xffff))
        } catch (_: Exception) {
        }
        d.complete(approved)
        return true
    }

    class PendingConsent internal constructor(
        val id: String,
        private val deferred: CompletableDeferred<Boolean>,
        private val appContext: Context,
    ) {
        suspend fun await(timeoutMs: Long = TIMEOUT_MS): Boolean {
            val ans = withTimeoutOrNull(timeoutMs) { deferred.await() }
            if (ans == null) {
                resolve(id, false)
                return false
            }
            return ans
        }
    }
}
