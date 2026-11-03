// MainActivity.kt — главный экран Rumix
// Создано: 18.10.2026 (Тиамат + Зая)

package com.rumix

import android.content.Intent
import android.os.Build
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Запускаем фоновый сервис (Shell)
        val serviceIntent = Intent(this, RumixForegroundService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }

        // Открываем Shell в WebView (или браузере)
        // Пока — просто закроем Activity, чтобы не мешать
        finish()
    }
}
