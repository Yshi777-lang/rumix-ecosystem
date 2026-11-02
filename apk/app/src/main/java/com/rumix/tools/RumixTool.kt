package com.rumix.tools

import android.app.Application
import com.rumix.RumixApp
import com.rumix.core.GateDecision
import com.rumix.core.GateLevel
import com.rumix.core.GateModeState
import com.rumix.core.PermissionGate
import com.rumix.core.RiskDetector

data class ArgSpec(
    val key: String,
    val label: String,
    val hint: String = "",
    val default: String = "",
    val required: Boolean = true,
)

data class ToolInput(val args: Map<String, String>) {
    fun get(key: String): String = args[key]?.trim() ?: ""
}

data class ToolResult(
    val ok: Boolean,
    val text: String,
    val status: String = if (ok) "full" else "error",
    val confidence: String = "high",
)

interface RumixTool {
    val id: String
    val title: String
    val description: String
    val icon: String
    val args: List<ArgSpec> get() = emptyList()
    val requiresBackend: Boolean get() = false
    val gated: Boolean get() = false
    val gateArg: String? get() = null

    suspend fun execute(input: ToolInput, ctx: ToolContext): ToolResult
}

class ToolContext(val app: Application) {

    val journal get() = RumixApp.instance.journal

    suspend fun gateCommand(command: String, source: String): Boolean {
        val decision: GateDecision = PermissionGate.classifyCommand(command)
        val risk = RiskDetector.detect(command)
        val verdict = GateModeState.resolve(decision)

        journal.record(
            source = source,
            test = "gate: $command",
            result = "${decision.level} → ${verdict.name}${if (risk.isDangerous) ", risk=${risk.level}: ${risk.description}" else ""}",
            status = "full",
            confidence = "high",
        )

        return when (verdict) {
            GateModeState.Verdict.ALLOW -> true
            GateModeState.Verdict.DENY -> {
                journal.record(source, "gate-deny: $command", decision.message, status = "full", confidence = "high")
                false
            }
            GateModeState.Verdict.ASK -> {
                val riskNote = if (risk.isDangerous) "⚠ ${risk.level}: ${risk.description}" else null
                val consent = com.rumix.core.ConsentManager.ask(
                    app,
                    title = "Врата: ${decision.level} — $command",
                    detail = decision.message,
                    level = decision.level,
                    riskNote = riskNote,
                )
                val approved = consent.await()
                journal.record(
                    source = source,
                    test = "consent: $command",
                    result = if (approved) "approved" else "denied/timeout",
                    status = "full",
                    confidence = "high",
                )
                approved
            }
        }
    }
}

object ToolRegistry {
    private val tools = LinkedHashMap<String, RumixTool>()

    val all: List<RumixTool> get() = synchronized(this) { tools.values.toList() }

    fun register(tool: RumixTool) {
        synchronized(this) { tools[tool.id] = tool }
    }

    fun loadFromServiceLoader(cl: ClassLoader) {
        val loader = java.util.ServiceLoader.load(RumixTool::class.java, cl)
        for (t in loader) register(t)
    }
}
