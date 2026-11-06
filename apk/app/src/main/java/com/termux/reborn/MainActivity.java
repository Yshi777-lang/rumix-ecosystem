package com.termux.reborn;
import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WebView webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        // В будущем здесь будет загрузка локального UI или подключение к 127.0.0.1:8001
        webView.loadUrl("file:///android_asset/index.html"); 
        setContentView(webView);
    }
}
