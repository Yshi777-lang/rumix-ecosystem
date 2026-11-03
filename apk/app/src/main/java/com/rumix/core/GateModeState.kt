package com.rumix.core

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

enum class GateMode(val ru: String) {
    DEFAULT("Спрашивать"),
    AUTO_APPROVE("Auto"),
    PLAN("Plan"),
}

data class PlanState(
    val active: Boolean = false,
    val text: String = "",
)

object GateModeState {
    private val _mode = MutableStateFlow(GateMode.DEFAULT)
    val mode: StateFlow<GateMode> = _mode

    private val _plan = MutableStateFlow(PlanState())
    val plan: StateFlow<PlanState> = _plan

    fun setMode(m: GateMode) {
        _mode.value = m
        if (m != GateMode.PLAN) _plan.value = PlanState(active = false)
        else if (!_plan.value.active) _plan.value = PlanState(active = true, text = _plan.value.text)
    }

    fun enterPlan(text: String = "") {
        _plan.value = PlanState(active = true, text = text)
        _mode.value = GateMode.PLAN
    }

    fun exitPlan() {
        _plan.value = PlanState(active = false)
        if (_mode.value == GateMode.PLAN) _mode.value = GateMode.DEFAULT
    }

    fun approvePlan() {
        _plan.value = PlanState(active = false)
        _mode.value = GateMode.DEFAULT
    }

    enum class Verdict { ALLOW, DENY, ASK }

    fun resolve(decision: GateDecision): Verdict {
        return when {
            !decision.allowed && decision.level == GateLevel.BLOCKED -> Verdict.DENY
            decision.level == GateLevel.READ || decision.allowed -> Verdict.ALLOW
            _mode.value == GateMode.AUTO_APPROVE -> Verdict.ALLOW
            _mode.value == GateMode.PLAN -> Verdict.DENY
            decision.needsConsent -> Verdict.ASK
            else -> Verdict.ASK
        }
    }
}
