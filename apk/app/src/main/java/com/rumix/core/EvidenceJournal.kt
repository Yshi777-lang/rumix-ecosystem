package com.rumix.core

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

data class EvidenceRecord(
    val source: String,
    val test: String,
    val result: String,
    val schemaVersion: Int = 1,
    val timestamp: String,
    val status: String = "full",
    val confidence: String = "medium",
    val limitations: List<String> = emptyList(),
    val rawRef: String? = null,
    val conflict: Boolean = false,
) {
    fun toJsonLine(): String = buildString {
        append('{')
        append("\"source\":\"").append(esc(source)).append('\"')
        append(",\"test\":\"").append(esc(test)).append('\"')
        append(",\"result\":\"").append(esc(result)).append('\"')
        append(",\"schema_version\":").append(schemaVersion)
        append(",\"timestamp\":\"").append(esc(timestamp)).append('\"')
        append(",\"status\":\"").append(esc(status)).append('\"')
        append(",\"confidence\":\"").append(esc(confidence)).append('\"')
        append(",\"limitations\":[")
        limitations.forEachIndexed { i, l ->
            if (i > 0) append(',')
            append('\"').append(esc(l)).append('\"')
        }
        append(']')
        append(",\"raw_ref\":")
        if (rawRef != null) append('\"').append(esc(rawRef)).append('\"') else append("null")
        append(",\"conflict\":").append(conflict)
        append('}')
    }

    private fun esc(s: String): String = buildString {
        for (c in s) when (c) {
            '\\' -> append("\\\\")
            '"' -> append("\\\"")
            '\n' -> append("\\n")
            '\r' -> append("\\r")
            '\t' -> append("\\t")
            else -> if (c.code < 0x20) append("\\u%04x".format(c.code)) else append(c)
        }
    }
}

class EvidenceJournal(private val file: File) {

    private val lock = Any()
    private val fmt = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US)

    fun record(
        source: String,
        test: String,
        result: String,
        status: String = "full",
        confidence: String = "medium",
        limitations: List<String> = emptyList(),
        rawRef: String? = null,
        conflict: Boolean = false,
    ): EvidenceRecord {
        val rec = EvidenceRecord(
            source = source, test = test, result = result,
            timestamp = fmt.format(Date()),
            status = status, confidence = confidence,
            limitations = limitations, rawRef = rawRef, conflict = conflict,
        )
        synchronized(lock) {
            file.parentFile?.mkdirs()
            file.appendText(rec.toJsonLine() + "\n", Charsets.UTF_8)
        }
        return rec
    }

    fun tailRaw(limit: Int = 50): List<String> = synchronized(lock) {
        if (!file.exists()) return emptyList()
        file.readLines(Charsets.UTF_8).filter { it.isNotBlank() }.takeLast(limit)
    }

    fun readAll(limit: Int = 200): List<EvidenceRecord> {
        val out = mutableListOf<EvidenceRecord>()
        for (line in tailRaw(limit)) {
            try {
                val o = JSONObject(line)
                val lim = o.optJSONArray("limitations")
                val limitations = mutableListOf<String>()
                if (lim != null) for (i in 0 until lim.length()) limitations.add(lim.optString(i))
                out.add(
                    EvidenceRecord(
                        source = o.optString("source"),
                        test = o.optString("test"),
                        result = o.optString("result"),
                        schemaVersion = o.optInt("schema_version", 1),
                        timestamp = o.optString("timestamp"),
                        status = o.optString("status", "full"),
                        confidence = o.optString("confidence", "medium"),
                        limitations = limitations,
                        rawRef = if (o.isNull("raw_ref")) null else o.optString("raw_ref"),
                        conflict = o.optBoolean("conflict", false),
                    )
                )
            } catch (_: Exception) {
            }
        }
        return out
    }

    fun count(): Int = synchronized(lock) {
        if (!file.exists()) 0 else file.readLines(Charsets.UTF_8).count { it.isNotBlank() }
    }
}
