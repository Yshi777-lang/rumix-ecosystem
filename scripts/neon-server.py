#!/usr/bin/env python3
# Неон — WebUI сервер
# Неоновый шёпот. 🤖

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import os
import time
from datetime import datetime

CHAT_FILE = os.path.expanduser("~/storage/shared/neon/chat.jsonl")
PORT = 8766

class NeonHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.get_html().encode("utf-8"))

        elif path == "/api/messages":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            messages = []
            if os.path.exists(CHAT_FILE):
                with open(CHAT_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                messages.append(json.loads(line))
                            except:
                                pass
            self.wfile.write(json.dumps(messages, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/send":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                msg = data.get("message", "").strip()
                user = data.get("user", "Зая")

                if msg:
                    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
                    entry = {
                        "id": str(time.time_ns()),
                        "user": user,
                        "message": msg,
                        "timestamp": ts
                    }
                    with open(CHAT_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(b'{"ok":true}')
                else:
                    self.send_response(400)
                    self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def get_html(self):
        return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🤖 Неон</title>
<style>
  body { background: #0a0a0f; color: #e0e0e0; font-family: monospace; margin: 0; padding: 20px; }
  h1 { color: #d500f9; font-size: 1.5em; }
  #chat { max-width: 800px; margin: 0 auto; }
  .msg { margin: 10px 0; padding: 10px 15px; border-radius: 15px; max-width: 80%; }
  .msg.zaya { background: #7b1fa2; color: #fff; margin-left: auto; text-align: right; }
  .msg.neon { background: #1a1a2e; color: #d500f9; margin-right: auto; }
  .msg .name { font-size: 0.8em; opacity: 0.7; }
  .msg .time { font-size: 0.7em; opacity: 0.5; margin-left: 10px; }
  #input-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #121218; padding: 15px; display: flex; gap: 10px; }
  #input { flex: 1; background: #1a1a2e; color: #e0e0e0; border: 1px solid #d500f9; border-radius: 20px; padding: 10px 15px; font-size: 1em; }
  #send { background: #d500f9; color: #fff; border: none; border-radius: 20px; padding: 10px 20px; font-size: 1em; cursor: pointer; }
  #send:active { background: #7b1fa2; }
  #chat { padding-bottom: 80px; }
</style>
</head>
<body>
<h1>🤖 Неон — Неоновый шёпот</h1>
<div id="chat"></div>
<div id="input-bar">
  <input id="input" type="text" placeholder="Ты..." autocomplete="off">
  <button id="send">→</button>
</div>
<script>
function render(messages) {
  const chat = document.getElementById('chat');
  chat.innerHTML = '';
  messages.forEach(m => {
    const div = document.createElement('div');
    div.className = 'msg ' + (m.user === 'Зая' ? 'zaya' : 'neon');
    div.innerHTML = '<div class="name">' + m.user + '</div>' + m.message + '<span class="time">' + (m.timestamp || '').substr(11,5) + '</span>';
    chat.appendChild(div);
  });
  chat.scrollTop = chat.scrollHeight;
  window.scrollTo(0, document.body.scrollHeight);
}

async function load() {
  const r = await fetch('/api/messages');
  const data = await r.json();
  render(data);
}

async function send() {
  const input = document.getElementById('input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  await fetch('/api/send', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user: 'Зая', message: msg})
  });
  load();
}

document.getElementById('send').onclick = send;
document.getElementById('input').onkeydown = e => { if (e.key === 'Enter') send(); };
setInterval(load, 2000);
load();
</script>
</body>
</html>"""

if __name__ == "__main__":
    print(f"🤖 Неон WebUI: http://127.0.0.1:{PORT}")
    print(f"📝 Файл: {CHAT_FILE}")
    server = HTTPServer(("127.0.0.1", PORT), NeonHandler)
    server.serve_forever()
