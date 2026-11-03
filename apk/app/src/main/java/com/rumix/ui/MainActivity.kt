package com.rumix.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.rumix.R
import com.rumix.RumixApp
import com.rumix.RumixForegroundService
import com.rumix.databinding.ActivityMainBinding
import com.rumix.net.HealthState
import com.rumix.net.RumixClient
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    private val tabs: Map<Int, Class<out Fragment>> = mapOf(
        R.id.nav_console to ConsoleFragment::class.java,
        R.id.nav_gate to GateFragment::class.java,
        R.id.nav_tools to ToolsFragment::class.java,
        R.id.nav_shell to ShellFragment::class.java,
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        askNotificationPermissionIfNeeded()
        startHouseService()

        binding.bottomNav.setOnItemSelectedListener { item ->
            switchTo(item.itemId)
            true
        }
        if (savedInstanceState == null) {
            switchTo(R.id.nav_console)
        }

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                while (true) {
                    val st = RumixClient.health()
                    renderChip(st)
                    delay(8_000)
                }
            }
        }

        binding.statusChip.setOnLongClickListener {
            showBackendDialog()
            true
        }
    }

    private fun switchTo(itemId: Int) {
        val targetCls = tabs[itemId] ?: return
        val targetTag = targetCls.simpleName
        val tx = supportFragmentManager.beginTransaction()
        for ((id, cls) in tabs) {
            val f = supportFragmentManager.findFragmentByTag(cls.simpleName) ?: continue
            if (id == itemId) tx.show(f) else tx.hide(f)
        }
        if (supportFragmentManager.findFragmentByTag(targetTag) == null) {
            val fragment = targetCls.getDeclaredConstructor().newInstance()
            tx.add(R.id.container, fragment, targetTag)
        }
        tx.commit()
    }

    private fun renderChip(st: HealthState) {
        val (text, color) = when (st) {
            HealthState.ONLINE -> getString(R.string.status_online) to ContextCompat.getColor(this, R.color.rumix_primary)
            HealthState.DEGRADED -> getString(R.string.status_degraded) to ContextCompat.getColor(this, R.color.rumix_warn)
            HealthState.OFFLINE -> getString(R.string.status_offline) to ContextCompat.getColor(this, R.color.rumix_danger)
            HealthState.CHECKING -> getString(R.string.status_checking) to ContextCompat.getColor(this, R.color.rumix_text_dim)
        }
        binding.statusChip.text = "● $text"
        binding.statusChip.setTextColor(color)
    }

    private fun askNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                ActivityCompat.requestPermissions(
                    this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), REQ_NOTIF
                )
            }
        }
    }

    private fun startHouseService() {
        val intent = Intent(this, RumixForegroundService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(intent)
        else startService(intent)
    }

    private fun showBackendDialog() {
        val input = EditText(this).apply {
            hint = "host:port"
            setText("${RumixClient.host}:${RumixClient.port}")
            setTextColor(ContextCompat.getColor(context, R.color.rumix_text))
            setHintTextColor(ContextCompat.getColor(context, R.color.rumix_text_dim))
        }
        AlertDialog.Builder(this)
            .setTitle("Адрес бэкенда")
            .setView(input)
            .setPositiveButton(R.string.ok) { _, _ ->
                val parts = (input.text?.toString() ?: "").trim().split(":")
                if (parts.size == 2 && parts[0].isNotBlank()) {
                    val port = parts[1].toIntOrNull() ?: RumixClient.DEFAULT_PORT
                    (application as RumixApp).saveBackend(parts[0], port)
                    Toast.makeText(this, "→ http://${parts[0]}:$port", Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(this, "Формат: host:port", Toast.LENGTH_SHORT).show()
                }
            }
            .setNegativeButton("Отмена", null)
            .show()
    }

    companion object {
        private const val REQ_NOTIF = 42
    }
}
