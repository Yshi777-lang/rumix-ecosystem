package com.rumix.core

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class ConsentReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val id = intent.getStringExtra(EXTRA_ID) ?: return
        val approved = intent.getBooleanExtra(EXTRA_APPROVE, false)
        ConsentManager.resolve(id, approved)
    }

    companion object {
        const val EXTRA_ID = "rumix.consent.id"
        const val EXTRA_APPROVE = "rumix.consent.approve"
    }
}
