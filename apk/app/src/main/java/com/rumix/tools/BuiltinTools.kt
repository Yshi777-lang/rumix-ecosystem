package com.rumix.tools

import com.rumix.core.PermissionGate
import com.rumix.net.RumixClient
import org.json.JSONArray
import org.json.JSONObject
import java.net.URLEncoder
import java.util.concurrent.TimeUnit

class ChatTool : RumixTool {
    override val id = "chat"
    override val title = "Чат с Неоном"
    override val description = "Спросить локальную модель (Qwen) через бэкенд"
    override val icon = "🤖"
    override val requiresBackend = true
    override val args = listOf(ArgSpec("message", "Сообщение", "Что спросить у Неона"))

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val reply = RumixClient.chat(input.get("message"))
        return ToolResult(true, reply)
    }
}

class StatusTool : RumixTool {
    override val id = "status"
    override val title = "Статус дома"
    override val description = "check-rumix.sh --json: regression, drift, loop"
    override val icon = "📊"
    override val requiresBackend = true

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val h = RumixClient.get("/api/status", readTimeout = 15_000)
        if (h.code != 200) return ToolResult(false, "HTTP ${h.code}: ${h.body.take(300)}")
        return try {
            ToolResult(true, JSONObject(h.body).toString(2))
        } catch (_: Exception) {
            ToolResult(true, h.body.take(1500), status = "partial")
        }
    }
}

class TranslateTool : RumixTool {
    override val id = "translate"
    override val title = "Перевод"
    override val description = "fxtranslate (Rust) на бэкенде"
    override val icon = "🌐"
    override val requiresBackend = true
    override val args = listOf(
        ArgSpec("text", "Текст", "Что перевести"),
        ArgSpec("src", "С языка", default = "en"),
        ArgSpec("trg", "На язык", default = "ru"),
    )

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val body = JSONObject()
            .put("text", input.get("text"))
            .put("src", input.get("src").ifEmpty { "en" })
            .put("trg", input.get("trg").ifEmpty { "ru" })
        val h = RumixClient.post("/api/translate", body)
        val o = JSONObject(h.body)
        if (h.code != 200 || o.has("error")) {
            return ToolResult(false, o.optString("error", "HTTP ${h.code}"))
        }
        return ToolResult(true, o.optString("result"))
    }
}

class FilesTool : RumixTool {
    override val id = "files"
    override val title = "Файлы"
    override val description = "Список каталога через file_gate бэкенда"
    override val icon = "📁"
    override val requiresBackend = true
    override val args = listOf(ArgSpec("path", "Путь", "Пусто = домашняя папка", required = false))

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val path = input.get("path")
        val url = "/api/files" + if (path.isNotEmpty())
            "?path=" + URLEncoder.encode(path, "UTF-8") else ""
        val h = RumixClient.get(url)
        val o = try { JSONObject(h.body) } catch (_: Exception) {
            return ToolResult(false, "HTTP ${h.code}: ${h.body.take(300)}")
        }
        if (o.has("error")) return ToolResult(false, o.optString("error"))
        val items = o.optJSONArray("items") ?: JSONArray()
        val sb = StringBuilder("📂 ${o.optString("path")}\n")
        for (i in 0 until items.length()) {
            val it = items.getJSONObject(i)
            val mark = if (it.optString("type") == "dir") "▸ " else "  "
            sb.append(mark).append(it.optString("name")).append('\n')
        }
        if (items.length() == 0) sb.append("(пусто)")
        return ToolResult(true, sb.toString())
    }
}

class WakeNeonTool : RumixTool {
    override val id = "wake_neon"
    override val title = "Разбудить Неона"
    override val description = "neon.sh start — поднять llama-server"
    override val icon = "⚡"
    override val requiresBackend = true

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val h = RumixClient.post("/api/neon/start", JSONObject())
        val o = try { JSONObject(h.body) } catch (_: Exception) { JSONObject() }
        val ok = o.optBoolean("ok", false)
        return ToolResult(ok, o.optString("output", o.optString("error", h.body.take(300))))
    }
}

class ShellTool : RumixTool {
    override val id = "shell"
    override val title = "Локальный shell"
    override val description = "Команды песочницы приложения. READ — авто, EXEC — согласие в шторке, BLOCKED — никогда."
    override val icon = "⌨"
    override val gated = true
    override val gateArg = "command"
    override val args = listOf(ArgSpec("command", "Команда", "напр. ls -la /sdcard  или  df"))

    private val SAFE = setOf(
        "ls", "cat", "pwd", "echo", "grep", "wc", "head", "tail",
        "ps", "df", "du", "free", "uptime", "whoami", "id", "date",
        "uname", "getprop", "env", "pgrep",
    )

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val cmd = input.get("command")
        val parts = cmd.split(Regex("""\s+""")).filter { it.isNotEmpty() }
        if (parts.isEmpty()) return ToolResult(false, "Пустая команда")
        val base = parts[0]
        if (base !in SAFE && base !in PermissionGate.EXEC_WHITELIST) {
            return ToolResult(false, "🚫 «$base» не в белом списке песочницы")
        }
        return try {
            val proc = ProcessBuilder(parts)
                .redirectErrorStream(true)
                .start()
            val finished = proc.waitFor(10, TimeUnit.SECONDS)
            if (!finished) {
                proc.destroyForcibly()
                return ToolResult(false, "⏱ Таймаут 10с — команда убита", status = "error")
            }
            val out = proc.inputStream.bufferedReader().readText()
            val tail = if (out.length > 4000) "…\n" + out.takeLast(4000) else out
            ToolResult(
                ok = proc.exitValue() == 0,
                text = tail.ifEmpty { "(нет вывода)" },
                status = if (proc.exitValue() == 0) "full" else "partial",
                confidence = "high",
            )
        } catch (e: Exception) {
            ToolResult(false, "Ошибка запуска: ${e.message}", status = "error", confidence = "medium")
        }
    }
}

class JournalTool : RumixTool {
    override val id = "journal"
    override val title = "Журнал улик"
    override val description = "Последние записи evidence.jsonl (append-only)"
    override val icon = "🧾"
    override val args = listOf(ArgSpec("limit", "Сколько записей", default = "20", required = false))

    override suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult {
        val limit = input.get("limit").toIntOrNull() ?: 20
        val recs = ctx.journal.readAll(limit)
        if (recs.isEmpty()) return ToolResult(true, "(журнал пуст)")
        val sb = StringBuilder()
        for (r in recs.asReversed()) {
            sb.append("• [").append(r.timestamp).append("] ")
                .append(r.source).append(" · ").append(r.confidence).append('\n')
                .append("  ").append(r.test).append(" → ").append(r.result).append('\n')
        }
        return ToolResult(true, sb.toString(), confidence = "high")
    }
}
