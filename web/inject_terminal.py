# inject_terminal.py — вставка терминала в Shell
# Создано: 17.10.2026 (Тиамат + Зая)

import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Добавляем окно терминала перед закрывающим тегом body
terminal_html = '''
<!-- Терминал (Победа 87) -->
<div id="terminal-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:9999; flex-direction:column; padding:20px; box-sizing:border-box;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <h3 style="color:#bb86fc; margin:0;">🌊 Rumix Terminal</h3>
    <button onclick="document.getElementById('terminal-modal').style.display='none'" style="background:#333; color:#fff; border:none; padding:5px 15px; border-radius:5px; cursor:pointer;">Закрыть</button>
  </div>
  <div id="terminal-output" style="flex:1; overflow-y:auto; background:#0a0a0a; color:#00ff00; font-family:monospace; padding:10px; border-radius:5px; margin-bottom:10px; white-space:pre-wrap;"></div>
  <div style="display:flex; gap:10px;">
    <input id="terminal-input" type="text" placeholder="Введите команду..." style="flex:1; padding:10px; background:#1a1a1a; color:#fff; border:1px solid #bb86fc; border-radius:5px; font-family:monospace;" onkeydown="if(event.key==='Enter') sendTerminalCommand()">
    <button onclick="sendTerminalCommand()" style="background:#bb86fc; color:#000; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">▶</button>
  </div>
</div>

<script>
async function openTerminal() {
  document.getElementById('terminal-modal').style.display = 'flex';
  document.getElementById('terminal-input').focus();
}

async function sendTerminalCommand() {
  const input = document.getElementById('terminal-input');
  const output = document.getElementById('terminal-output');
  const cmd = input.value.trim();
  if (!cmd) return;

  output.innerHTML += `\\n<span style="color:#bb86fc;">$ ${cmd}</span>\\n`;
  input.value = '';

  try {
    const res = await fetch('/api/terminal', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({cmd: cmd})
    });
    const data = await res.json();
    
    if (data.status === 'OK' || data.status === 'READ') {
      output.innerHTML += `<span style="color:#00ff00;">${data.output || '(пусто)'}</span>\\n`;
    } else {
      output.innerHTML += `<span style="color:#ff5555;">🚫 ${data.message}</span>\\n`;
    }
  } catch (e) {
    output.innerHTML += `<span style="color:#ff5555;">Ошибка: ${e.message}</span>\\n`;
  }
  
  output.scrollTop = output.scrollHeight;
}
</script>
'''

html = html.replace('</body>', terminal_html + '\n</body>')

# 2. Заменяем кнопку "Терминал (в Rumix)" на вызов openTerminal()
html = html.replace(
    "if (id === 'terminal') {\n    // Открыть Termux через intent\n    window.location.href = 'intent://#Intent;package=com.rumix;end';\n  } else",
    "if (id === 'terminal') {\n    openTerminal();\n  } else"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ Терминал встроен в Shell (HTML + JS).')
