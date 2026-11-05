package com.rumix.net

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

enum class HealthState { ONLINE, DEGRADED, OFFLINE, CHECKING }

object RumixClient {
    const val DEFAULT_HOST = "127.0.0.1"
    const val DEFAULT_PORT = 8001

    var host: String = DEFAULT_HOST
    var port: Int = DEFAULT_PORT

    val baseUrl: String get() = "http://$host:$port"

    /** Токен установки (~/.rumix_token на стороне Shell). Пусто = старый режим без токена. */
    var token: String = ""

    /** Стартовый адрес Shell: токен один раз в query → сервер ставит cookie для WebView. */
    val shellUrl: String
        get() = if (token.isBlank()) "$baseUrl/"
        else "$baseUrl/?t=" + URLEncoder.encode(token, "UTF-8")

    data class Http(val code: Int, val body: String)

    private fun open(url: String, method: String, body: String?, readTimeout: Int): HttpURLConnection {
        val conn = URL(url) as HttpURLConnection
        conn.requestMethod = method
        conn.connectTimeout = 3_000
        conn.readTimeout = readTimeout
        conn.setRequestProperty("Accept", "application/json")
        if (token.isNotBlank()) conn.setRequestProperty("X-Rumix-Token", token)
        if (body != null) {
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
        }
        return conn
    }

    private fun readAll(conn: HttpURLConnection): String {
        val stream = if (conn.responseCode in 200..399) conn.inputStream else conn.errorStream
        return stream?.bufferedReader()?.use(BufferedReader::readText) ?: ""
    }

    suspend fun get(path: String, readTimeout: Int = 10_000): Http = withContext(Dispatchers.IO) {
        val conn = open(baseUrl + path, "GET", null, readTimeout)
        try {
            Http(conn.responseCode, readAll(conn))
        } finally {
            conn.disconnect()
        }
    }

    suspend fun post(path: String, json: JSONObject, readTimeout: Int = 30_000): Http =
        withContext(Dispatchers.IO) {
            val conn = open(baseUrl + path, "POST", json.toString(), readTimeout)
            try {
                Http(conn.responseCode, readAll(conn))
            } finally {
                conn.disconnect()
            }
        }

    suspend fun health(): HealthState = withContext(Dispatchers.IO) {
        try {
            val conn = open("$baseUrl/api/agent/status", "GET", null, 2_500)
            val code = conn.responseCode
            conn.disconnect()
            if (code !in 200..399) return@withContext HealthState.DEGRADED

            val probe = open("$baseUrl/api/modules", "GET", null, 2_500)
            val probeCode = probe.responseCode
            probe.disconnect()
            if (probeCode == 401) HealthState.DEGRADED else HealthState.ONLINE
        } catch (_: Exception) {
            HealthState.OFFLINE
        }
    }

    suspend fun chat(message: String): String {
        val h = post("/api/chat", JSONObject().put("message", message), readTimeout = 120_000)
        val o = try {
            JSONObject(h.body)
        } catch (_: Exception) {
            throw IllegalStateException("Бэкенд ответил не-JSON (HTTP ${h.code})")
        }
        if (h.code !in 200..399 || o.has("error")) {
            throw IllegalStateException(o.optString("error", "Неон не ответил (HTTP ${h.code})"))
        }
        return o.optString("reply", o.optString("response", ""))
    }
}
