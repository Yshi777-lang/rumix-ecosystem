package com.termux.reborn;
import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;
public class TermuxVpnService extends Service {
    @Override
    public IBinder onBind(Intent intent) { return null; }
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && "START_VPN".equals(intent.getAction())) {
            Log.i("TermuxVpnService", "VPN Start Requested (Stub)");
            // Здесь будет логика запуска Xray + hev-socks5-tunnel через ProcessBuilder и VpnService.Builder
        }
        return START_STICKY;
    }
}
