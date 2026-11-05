package com.rumix.ui

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.rumix.RumixApp
import com.rumix.databinding.FragmentShellBinding
import com.rumix.net.HealthState
import com.rumix.net.RumixClient
import kotlinx.coroutines.launch

class ShellFragment : Fragment() {

    private var _binding: FragmentShellBinding? = null
    private val binding get() = _binding!!
    private var loaded = false

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentShellBinding.inflate(inflater, container, false)
        return binding.root
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.webview.settings.javaScriptEnabled = true
        binding.webview.settings.domStorageEnabled = true
        binding.webview.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView?, request: WebResourceRequest?
            ): Boolean = false

            override fun onReceivedError(
                view: WebView?, request: WebResourceRequest?, error: android.webkit.WebResourceError?
            ) {
                if (request?.isForMainFrame == true) showOffline()
            }
        }
        binding.retry.setOnClickListener { loaded = false; connect() }
    }

    override fun onResume() {
        super.onResume()
        connect()
    }

    private fun connect() {
        if (loaded) return
        viewLifecycleOwner.lifecycleScope.launch {
            val st = RumixClient.health()
            if (st == HealthState.OFFLINE) {
                showOffline()
            } else {
                loaded = true
                binding.offlinePanel.visibility = View.GONE
                binding.webview.visibility = View.VISIBLE
                binding.webview.loadUrl(RumixClient.shellUrl)
            }
        }
    }

    private fun showOffline() {
        loaded = false
        binding.webview.visibility = View.GONE
        binding.offlinePanel.visibility = View.VISIBLE
        (requireActivity().application as RumixApp).journal.record(
            source = "shell",
            test = "connect ${RumixClient.baseUrl}",
            result = "бэкенд недоступен",
            status = "unavailable",
            confidence = "high",
        )
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
