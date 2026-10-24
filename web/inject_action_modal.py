with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

modal_html = '''
<!-- Модальное окно для действий -->
<div id="action-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:9999; flex-direction:column; padding:20px; box-sizing:border-box;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <h3 id="action-title" style="color:#bb86fc; margin:0;">Результат</h3>
    <button onclick="document.getElementById('action-modal').style.display='none'" style="background:#333; color:#fff; border:none; padding:5px 15px; border-radius:5px; cursor:pointer;">Закрыть</button>
  </div>
  <pre id="action-output" style="flex:1; overflow-y:auto; background:#0a0a0a; color:#00ff00; font-family:monospace; padding:10px; border-radius:5px; white-space:pre-wrap; font-size:12px;"></pre>
</div>

<script>
async function runAction(a) {
  const modal = document.getElementById('action-modal');
  const title = document.getElementById('action-title');
  const output = document.getElementById('action-output');
  title.innerText = '⏳ ' + a + '...';
  output.innerText = 'Загрузка...';
  modal.style.display = 'flex';

  try {
    const r = await fetch('/api/action', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({action: a})
    });
    const d = await r.json();
    title.innerText = (d.ok ? '✅ ' : '❌ ') + a;
    output.innerText = d.stdout || d.stderr || d.error || 'Нет вывода';
  } catch (e) {
    title.innerText = '❌ Ошибка';
    output.innerText = 'Ошибка связи с бэкендом: ' + e.message;
  }
}
</script>
'''

# Удаляем старую функцию runAction (если есть)
import re
html = re.sub(r'async function runAction\(a\)\{.*?\n\}', '', html, flags=re.DOTALL)

# Вставляем новую модалку перед </body>
html = html.replace('</body>', modal_html + '\n</body>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('✅ Модальное окно для действий добавлено.')
