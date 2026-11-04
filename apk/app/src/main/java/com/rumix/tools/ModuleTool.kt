package com.rumix.tools

import com.rumix.net.RumixClient
import org.json.JSONObject

/**
 * Универсальный тул для модулей бэкенда (core/modules/).
 * Один тул на все модули: появился новый Python-файл — карточка в APK уже работает,
 * пересборка не нужна.
 *  - пустой module                     → каталог /api/modules
 *  - module=battery                    → GET  /api/m/battery
 *  - module=voice + payload={"set":…}  → POST /api/m/voice
 */
class ModuleTool : RumixTool {
    override val id = "module"
    override val title = "Модули"
    override val description = "Плагины бэкенда: battery, voice, stt, uptime… Пусто = каталог"
    override val icon = "🧩"
    override val requiresBackend = true
    override val args = listOf(
        ArgSpec("module", "Модуль", "battery | voice | stt | uptime. Пусто = каталог", required = false),
        ArgSpec("payload", "JSON-тело", "для действия: {\"set\":{\"lang\":\"en\"}}. Пусто = GET", required = false),
    )

    /** Модули, которым мало обычных 30 с: запись + whisper + конвертация. */
    private val slow = mapOf("stt" to 300_000, "sd" to 300_000)

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val name = input.get("module")
        val payload = input.get("payload")

        if (name.isEmpty()) return catalog()

        val timeout = slow[name] ?: 30_000
        val h = if (payload.isEmpty()) {
            RumixClient.get("/api/m/$name", readTimeout = timeout)
        } else {
            val body = try {
                JSONObject(payload)
            } catch (e: Exception) {
                return ToolResult(false, "Невалидный JSON: ${e.message}", status = "partial")
            }
            RumixClient.post("/api/m/$name", body, readTimeout = timeout)
        }

        val o = try {
            JSONObject(h.body)
        } catch (_: Exception) {
            // не JSON (например, прокси/ошибка Flask) — отдаём как есть, но честно
            return ToolResult(h.code in 200..299, "HTTP ${h.code}: ${h.body.take(600)}", status = "partial")
        }

        val ok = o.optBoolean("ok", h.code in 200..299)
        val status = o.optString("status", if (ok) "full" else "error")
        val data = o.opt("data") ?: o.opt("error") ?: h.body
        val text = if (data is JSONObject) data.toString(2) else data.toString()

        val limits = o.optJSONArray("limitations")
        val suffix = if (limits != null && limits.length() > 0)
            "\n⚠ " + (0 until limits.length()).joinToString("\n⚠ ") { limits.getString(it) }
        else ""

        return ToolResult(ok, text + suffix, status = status, confidence = "high")
    }

    /** Каталог: значок, имя, заголовок, ✓/✗ и текст ошибки у сломанных. */
    private suspend fun catalog(): ToolResult {
        val h = RumixClient.get("/api/modules", readTimeout = 10_000)
        if (h.code != 200) return ToolResult(false, "HTTP ${h.code}: ${h.body.take(300)}")
        return try {
            val arr = JSONObject(h.body).getJSONArray("modules")
            val sb = StringBuilder("🧩 Модули бэкенда\n")
            for (i in 0 until arr.length()) {
                val o = arr.getJSONObject(i)
                sb.append(o.optString("icon")).append(' ')
                    .append(o.optString("name")).append(" — ")
                    .append(o.optString("title"))
                    .append(if (o.optBoolean("ok")) " ✓" else " ✗")
                    .append(if (o.optBoolean("has_action")) " ▶" else "")
                    .append('\n')
                val help = o.optString("help")
                if (help.isNotEmpty()) sb.append("    ").append(help).append('\n')
                val err = o.optString("error")
                if (err.isNotEmpty()) sb.append("    ⚠ ").append(err).append('\n')
            }
            ToolResult(true, sb.toString())
        } catch (_: Exception) {
            ToolResult(true, h.body.take(1500), status = "partial")
        }
    }
}
