package com.rumix.ui

import android.os.Bundle
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.rumix.RumixApp
import com.rumix.databinding.FragmentConsoleBinding
import com.rumix.net.RumixClient
import kotlinx.coroutines.launch

class ConsoleFragment : Fragment() {

    private var _binding: FragmentConsoleBinding? = null
    private val binding get() = _binding!!

    private val messages = mutableListOf<Msg>()
    private lateinit var adapter: MessageAdapter

    enum class Role { USER, NEON, SYS }
    data class Msg(val role: Role, val text: String)

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentConsoleBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        adapter = MessageAdapter(messages)
        binding.messages.layoutManager = LinearLayoutManager(requireContext()).apply {
            stackFromEnd = true
        }
        binding.messages.adapter = adapter

        if (messages.isEmpty()) {
            add(Role.SYS, "[SYSTEM] Rumix Core запущен. Врата открыты, журнал пишется.")
        }

        binding.send.setOnClickListener { sendChat() }
        binding.wake.setOnClickListener { wakeNeon() }
    }

    private fun sendChat() {
        val text = binding.input.text?.toString()?.trim().orEmpty()
        if (text.isEmpty()) return
        binding.input.text?.clear()
        add(Role.USER, text)
        val thinkingIdx = add(Role.SYS, "🤖 Неон думает…")

        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val reply = RumixClient.chat(text)
                replaceAt(thinkingIdx, Role.NEON, reply)
                (requireActivity().application as RumixApp).journal.record(
                    source = "neon",
                    test = "chat",
                    result = reply.take(200),
                    status = "full",
                    confidence = "low",
                    limitations = listOf("ответ локальной модели, не верифицирован"),
                )
            } catch (e: Exception) {
                replaceAt(thinkingIdx, Role.SYS, "❌ ${e.message}")
                (requireActivity().application as RumixApp).journal.record(
                    source = "console",
                    test = "chat",
                    result = e.message ?: "error",
                    status = "error",
                    confidence = "medium",
                )
            }
        }
    }

    private fun wakeNeon() {
        add(Role.SYS, "⚡ пробуждаю Неона…")
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val h = RumixClient.post("/api/neon/start", org.json.JSONObject())
                val body = try {
                    org.json.JSONObject(h.body)
                } catch (_: Exception) {
                    org.json.JSONObject()
                }
                val ok = body.optBoolean("ok", false)
                add(Role.SYS, if (ok) "✅ ${body.optString("output", "Неон проснулся")}"
                             else "❌ ${body.optString("error", "HTTP ${h.code}")}")
            } catch (e: Exception) {
                add(Role.SYS, "❌ ${e.message}")
            }
        }
    }

    private fun add(role: Role, text: String): Int {
        messages.add(Msg(role, text))
        adapter.notifyItemInserted(messages.lastIndex)
        binding.messages.scrollToPosition(messages.lastIndex)
        return messages.lastIndex
    }

    private fun replaceAt(idx: Int, role: Role, text: String) {
        if (idx !in messages.indices) {
            add(role, text); return
        }
        messages[idx] = Msg(role, text)
        adapter.notifyItemChanged(idx)
        binding.messages.scrollToPosition(messages.lastIndex)
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private inner class MessageAdapter(
        private val items: List<Msg>,
    ) : RecyclerView.Adapter<MessageAdapter.VH>() {

        inner class VH(val v: View) : RecyclerView.ViewHolder(v) {
            val bubble: android.widget.TextView = v.findViewById(com.rumix.R.id.bubble)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val v = LayoutInflater.from(parent.context)
                .inflate(com.rumix.R.layout.item_message, parent, false)
            return VH(v)
        }

        override fun getItemCount(): Int = items.size

        override fun onBindViewHolder(holder: VH, position: Int) {
            val m = items[position]
            holder.bubble.text = m.text
            val lp = holder.bubble.layoutParams as LinearLayout.LayoutParams
            when (m.role) {
                Role.USER -> {
                    lp.gravity = Gravity.END
                    holder.bubble.setBackgroundResource(com.rumix.R.drawable.bubble_user)
                    holder.bubble.setTextColor(
                        ContextCompat.getColor(holder.itemView.context, com.rumix.R.color.rumix_text)
                    )
                }
                Role.NEON -> {
                    lp.gravity = Gravity.START
                    holder.bubble.setBackgroundResource(com.rumix.R.drawable.bubble_neon)
                    holder.bubble.setTextColor(
                        ContextCompat.getColor(holder.itemView.context, com.rumix.R.color.rumix_primary)
                    )
                }
                Role.SYS -> {
                    lp.gravity = Gravity.START
                    holder.bubble.setBackgroundResource(com.rumix.R.drawable.bubble_neon)
                    holder.bubble.setTextColor(
                        ContextCompat.getColor(holder.itemView.context, com.rumix.R.color.rumix_text_dim)
                    )
                }
            }
            holder.bubble.layoutParams = lp
        }
    }
}
