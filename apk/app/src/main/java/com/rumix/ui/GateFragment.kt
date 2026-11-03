package com.rumix.ui

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.app.AlertDialog
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.rumix.R
import com.rumix.RumixApp
import com.rumix.core.ConsentManager
import com.rumix.core.GateLevel
import com.rumix.core.GateMode
import com.rumix.core.GateModeState
import com.rumix.core.PermissionGate
import com.rumix.core.RiskDetector
import com.rumix.core.RiskLevel
import com.rumix.databinding.FragmentGateBinding
import com.rumix.databinding.ItemConsentBinding
import kotlinx.coroutines.launch

class GateFragment : Fragment() {

    private var _binding: FragmentGateBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentGateBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        setupModes()
        setupPlan()
        setupPlayground()
        setupJournal()
        observeState()
    }

    private fun setupModes() {
        binding.modeGroup.check(R.id.mode_default)
        binding.modeGroup.addOnButtonCheckedListener { _, id ->
            if (id != binding.modeGroup.checkedButtonId) return@addOnButtonCheckedListener
            val mode = when (id) {
                R.id.mode_auto -> GateMode.AUTO_APPROVE
                R.id.mode_plan -> GateMode.PLAN
                else -> GateMode.DEFAULT
            }
            if (mode == GateMode.PLAN && GateModeState.plan.value.active) {
                GateModeState.setMode(GateMode.PLAN)
            } else if (mode == GateMode.PLAN) {
                GateModeState.enterPlan(GateModeState.plan.value.text)
            } else {
                GateModeState.setMode(mode)
            }
        }
    }

    private fun setupPlan() {
        binding.planAction.setOnClickListener {
            val plan = GateModeState.plan.value
            when {
                plan.active -> GateModeState.approvePlan()
                GateModeState.mode.value == GateMode.PLAN -> GateModeState.exitPlan()
                else -> GateModeState.enterPlan("")
            }
            refreshPlanUi()
        }
    }

    private fun refreshPlanUi() {
        val plan = GateModeState.plan.value
        val mode = GateModeState.mode.value
        if (plan.active || mode == GateMode.PLAN) {
            binding.planStatus.text = getString(R.string.gate_plan_active)
            binding.planStatus.setTextColor(
                ContextCompat.getColor(requireContext(), R.color.rumix_warn)
            )
            binding.planAction.text =
                if (plan.active) getString(R.string.gate_plan_approve) else getString(R.string.gate_plan_exit)
        } else {
            binding.planStatus.text = getString(R.string.gate_plan_inactive)
            binding.planStatus.setTextColor(
                ContextCompat.getColor(requireContext(), R.color.rumix_text)
            )
            binding.planAction.text = getString(R.string.gate_plan_enter)
        }
        val want = when (mode) {
            GateMode.AUTO_APPROVE -> R.id.mode_auto
            GateMode.PLAN -> R.id.mode_plan
            else -> R.id.mode_default
        }
        if (binding.modeGroup.checkedButtonId != want) binding.modeGroup.check(want)
    }

    private fun setupPlayground() {
        binding.playInput.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun onTextChanged(s: CharSequence?, a: Int, b: Int, c: Int) {}
            override fun afterTextChanged(s: Editable?) = renderVerdict(s?.toString().orEmpty())
        })
    }

    private fun renderVerdict(cmd: String) {
        val tv = binding.playVerdict
        if (cmd.isBlank()) {
            tv.text = "…"
            tv.setTextColor(color(R.color.rumix_text_dim))
            return
        }
        val decision = PermissionGate.classifyCommand(cmd)
        val risk = RiskDetector.detect(cmd)
        val head = when {
            decision.level == GateLevel.BLOCKED -> "🚫 BLOCKED — всегда запрет"
            decision.level == GateLevel.READ -> "🟢 READ — авто, без вопроса"
            decision.whitelisted -> "🟡 EXEC (whitelist) — авто"
            else -> "🔴 EXEC — спросит согласия (60с → отказ)"
        }
        val riskLine = if (risk.isDangerous) {
            "\n⚠ риск ${risk.level}: ${risk.description} · «${risk.matched}»"
        } else {
            "\n✅ риск LOW"
        }
        tv.text = head + riskLine + "\n" + decision.message
        tv.setTextColor(
            color(
                when {
                    decision.level == GateLevel.BLOCKED -> R.color.rumix_danger
                    decision.level == GateLevel.READ || decision.whitelisted -> R.color.rumix_primary
                    risk.level == RiskLevel.HIGH -> R.color.rumix_danger
                    else -> R.color.rumix_warn
                }
            )
        )
    }

    private fun setupJournal() {
        binding.journalRefresh.setOnClickListener { refreshJournal() }
        binding.journalFull.setOnClickListener {
            val recs = journal().readAll(100)
            val text = recs.asReversed().joinToString("\n\n") {
                "[${it.timestamp}] ${it.source} · ${it.confidence}\n${it.test}\n→ ${it.result}"
            }.ifEmpty { getString(R.string.gate_journal_empty) }
            AlertDialog.Builder(requireContext())
                .setTitle(R.string.gate_journal)
                .setMessage(text)
                .setPositiveButton(R.string.tools_close, null)
                .show()
        }
    }

    private fun refreshJournal() {
        val recs = journal().readAll(5)
        val text = recs.asReversed().joinToString("\n\n") {
            "[${it.timestamp}] ${it.source} · ${it.confidence}\n${it.test} → ${it.result}"
        }.ifEmpty { getString(R.string.gate_journal_empty) }
        binding.journalPreview.text = text
    }

    private fun journal() = (requireActivity().application as RumixApp).journal

    private fun observeState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch { GateModeState.mode.collect { refreshPlanUi() } }
                launch { GateModeState.plan.collect { refreshPlanUi() } }
                launch { ConsentManager.pending.collect { list -> renderConsents(list) } }
            }
        }
    }

    private fun renderConsents(list: List<ConsentManager.Pending>) {
        binding.consentEmpty.visibility = if (list.isEmpty()) View.VISIBLE else View.GONE
        binding.consentList.removeAllViews()
        for (p in list) {
            val row = ItemConsentBinding.inflate(layoutInflater, binding.consentList, false)
            row.consentTitle.text = "${p.level}: ${p.title}"
            row.consentDetail.text = p.detail
            row.consentRisk.text = p.riskNote ?: ""
            row.consentYes.setOnClickListener { ConsentManager.resolve(p.id, true) }
            row.consentNo.setOnClickListener { ConsentManager.resolve(p.id, false) }
            binding.consentList.addView(row.root)
        }
    }

    private fun color(res: Int) = ContextCompat.getColor(requireContext(), res)

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
