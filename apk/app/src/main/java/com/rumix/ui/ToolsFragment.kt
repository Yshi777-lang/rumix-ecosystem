package com.rumix.ui

import android.os.Bundle
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.rumix.R
import com.rumix.RumixApp
import com.rumix.databinding.FragmentToolsBinding
import com.rumix.databinding.ItemToolBinding
import com.rumix.net.RumixClient
import com.rumix.tools.ArgSpec
import com.rumix.tools.RumixTool
import com.rumix.tools.ToolContext
import com.rumix.tools.ToolInput
import com.rumix.tools.ToolRegistry
import kotlinx.coroutines.launch

class ToolsFragment : Fragment() {

    private var _binding: FragmentToolsBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentToolsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.toolsList.layoutManager = LinearLayoutManager(requireContext())
        binding.toolsList.adapter = ToolAdapter(ToolRegistry.all)
    }

    private fun onRun(tool: RumixTool) {
        if (tool.args.isEmpty()) {
            execute(tool, emptyMap())
        } else {
            showArgsDialog(tool)
        }
    }

    private fun showArgsDialog(tool: RumixTool) {
        val pad = (16 * resources.displayMetrics.density).toInt()
        val box = LinearLayout(requireContext()).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(pad, pad / 2, pad, 0)
        }
        val fields = LinkedHashMap<ArgSpec, EditText>()
        for (spec in tool.args) {
            val label = TextView(requireContext()).apply {
                text = spec.label
                setTextColor(ContextCompat.getColor(context, R.color.rumix_primary))
                textSize = 12f
            }
            val edit = EditText(requireContext()).apply {
                hint = spec.hint
                setText(spec.default)
                setTextColor(ContextCompat.getColor(context, R.color.rumix_text))
                setHintTextColor(ContextCompat.getColor(context, R.color.rumix_text_dim))
                isSingleLine = spec.key != "message" && spec.key != "text"
                if (spec.key == "message" || spec.key == "text") minLines = 2
            }
            box.addView(label)
            box.addView(edit)
            fields[spec] = edit
        }
        val scroll = ScrollView(requireContext()).apply { addView(box) }
        AlertDialog.Builder(requireContext())
            .setTitle("${tool.icon} ${tool.title}")
            .setView(scroll)
            .setPositiveButton(R.string.tools_run) { _, _ ->
                val args = HashMap<String, String>()
                var missing: String? = null
                for ((spec, edit) in fields) {
                    val v = edit.text?.toString()?.trim().orEmpty()
                    if (v.isEmpty() && spec.required && missing == null) missing = spec.label
                    args[spec.key] = v
                }
                if (missing != null) {
                    Toast.makeText(requireContext(), "Нужен: $missing", Toast.LENGTH_SHORT).show()
                } else {
                    execute(tool, args)
                }
            }
            .setNegativeButton(R.string.tools_close, null)
            .show()
    }

    private fun execute(tool: RumixTool, args: Map<String, String>) {
        Toast.makeText(requireContext(), "выполняю ${tool.id}…", Toast.LENGTH_SHORT).show()
        viewLifecycleOwner.lifecycleScope.launch {
            if (tool.requiresBackend && RumixClient.health() != com.rumix.net.HealthState.ONLINE) {
                showResult(tool, com.rumix.tools.ToolResult(
                    false,
                    getString(R.string.tools_needs_backend) + "\n" + RumixClient.baseUrl,
                    status = "unavailable",
                    confidence = "high",
                ))
                return@launch
            }

            val ctx = ToolContext(requireActivity().application)

            if (tool.gated && tool.gateArg != null) {
                val cmd = args[tool.gateArg].orEmpty()
                val passed = ctx.gateCommand(cmd, tool.id)
                if (!passed) {
                    val res = com.rumix.tools.ToolResult(
                        false, "🚫 Врата закрыли команду (BLOCKED / PLAN / отказ)",
                        status = "unavailable", confidence = "high",
                    )
                    showResult(tool, res)
                    return@launch
                }
            }

            val res = try {
                tool.execute(ToolInput(args), ctx)
            } catch (e: Exception) {
                com.rumix.tools.ToolResult(
                    false, e.message ?: "Ошибка", status = "error", confidence = "medium"
                )
            }
            ctx.journal.record(
                source = tool.id,
                test = "run: " + (args.values.joinToString(" ").ifEmpty { "(без аргументов)" }),
                result = res.text.take(300),
                status = res.status,
                confidence = res.confidence,
            )
            showResult(tool, res)
        }
    }

    private fun showResult(tool: RumixTool, res: com.rumix.tools.ToolResult) {
        val tv = TextView(requireContext()).apply {
            text = res.text
            setTextColor(
                ContextCompat.getColor(
                    context,
                    if (res.ok) R.color.rumix_text else R.color.rumix_danger
                )
            )
            typeface = android.graphics.Typeface.MONOSPACE
            textSize = 13f
            setTextIsSelectable(true)
            val pad = (14 * resources.displayMetrics.density).toInt()
            setPadding(pad, pad, pad, pad)
        }
        val scroll = ScrollView(requireContext()).apply {
            addView(tv)
            isFillViewport = true
        }
        AlertDialog.Builder(requireContext())
            .setTitle("${if (res.ok) "✅" else "❌"} ${tool.title}")
            .setView(scroll)
            .setPositiveButton(R.string.tools_close, null)
            .show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private inner class ToolAdapter(
        private val items: List<RumixTool>,
    ) : RecyclerView.Adapter<ToolAdapter.VH>() {

        inner class VH(val b: ItemToolBinding) : RecyclerView.ViewHolder(b.root)

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH =
            VH(ItemToolBinding.inflate(LayoutInflater.from(parent.context), parent, false))

        override fun getItemCount(): Int = items.size

        override fun onBindViewHolder(holder: VH, position: Int) {
            val tool = items[position]
            holder.b.toolIcon.text = tool.icon
            holder.b.toolTitle.text = tool.title
            holder.b.toolDesc.text = buildString {
                append(tool.description)
                if (tool.requiresBackend) append(" · 📡")
                if (tool.gated) append(" · 🛡")
            }
            holder.b.toolRun.setOnClickListener { onRun(tool) }
            holder.b.root.setOnClickListener { onRun(tool) }
        }
    }
}
