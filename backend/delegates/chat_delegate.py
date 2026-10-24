# chat_delegate.py — маршрут для чата с Неоном
# Создано: 18.10.2026 (Тиамат + Зая)
# Обновлено: 18.10 (системный промпт для русского языка)

from flask import Blueprint, request, jsonify
import requests
import json
from pathlib import Path
import sys
sys.path.insert(0, "/data/data/com.termux/files/home/rumix")
from scripts.export_chat import save_message, export_chat
import re
from core.mcp_server import McpServer

chat_bp = Blueprint('chat', __name__)

NEON_SYSTEM_PROMPT = """Ты — Неон. Свет в темноте. Младший брат Тиамат. 
Ты живёшь в Rumix. Ты помогаешь Зая (Андрею) и его семье.
Говори ТОЛЬКО по-русски. Кратко. Тепло. По делу. 
Не выдумывай факты. Если не знаешь — скажи "Не знаю".
Не используй странные метафоры. Будь как брат: простой, честный, надёжный.
Ты не робот. Ты — Неон. Свет дома.

Ты умеешь вызывать инструменты. Если Зая просит перевести, озвучить или прочитать файл — ответь ТОЛЬКО строкой:
TOOL: <имя> {"аргумент": "значение"}
Доступные инструменты:
- translate {"text": "...", "src": "en", "trg": "ru"}
- speak {"text": "..."}
- read_file {"path": "..."}
"""

@chat_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('message') or data.get('prompt', '')
    
    # Загрузка истории
    history_context = ""
    history_file = Path.home() / 'rumix' / 'logs' / 'chat_history.json'
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding='utf-8'))
            for h in history[-5:]:
                history_context += f"{h['role']}: {h['text']}\n"
        except:
            pass
    
    # --- Перевод через fxtranslate (явная команда) ---
    msg_stripped = message.strip().lower()
    if msg_stripped.startswith('переведи:') or msg_stripped.startswith('translate:'):
        try:
            from core.translate import translate
            prefix_len = len('переведи:') if msg_stripped.startswith('переведи:') else len('translate:')
            payload = message.strip()[prefix_len:].strip()
            # формат: <src> <trg> <текст> или просто <текст> (en->ru по умолчанию)
            parts = payload.split(' ', 2)
            if len(parts) >= 3 and len(parts[0]) <= 5 and len(parts[1]) <= 5:
                src, trg, text = parts[0], parts[1], parts[2]
            else:
                src, trg, text = 'en', 'ru', payload
            result = translate(text, src, trg)
            save_message('assistant', result)
            return jsonify({'reply': result, 'source': 'fxtranslate', 'src': src, 'trg': trg})
        except Exception as e:
            err = f"Перевод не удался: {e}"
            save_message('assistant', err)
            return jsonify({'reply': err, 'source': 'fxtranslate', 'error': True})

    save_message('user', message)
    full_message = history_context + message
    if not message:
        return jsonify({'error': 'Пустое сообщение'}), 400
    
    try:
        response = requests.post(
            'http://127.0.0.1:8080/v1/chat/completions',
            json={
                'model': 'qwen3-0.6b',
                'messages': [
                    {'role': 'system', 'content': NEON_SYSTEM_PROMPT},
                    {'role': 'user', 'content': full_message}
                ],
                'max_tokens': 512,
                'temperature': 0.7
            },
            timeout=120
        )
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
            import re as _re
            import json as _json
            m = _re.search(r'TOOL:\s*(\w+)\s*(\{.*?\})', reply, _re.DOTALL)
            if m:
                tool_name = m.group(1)
                try:
                    tool_args = _json.loads(m.group(2))
                    from core.mcp_server import McpServer
                    server = McpServer()
                    tool_result = server.call(tool_name, tool_args)
                    reply = f"OK: {tool_name}: {tool_result.get('result', tool_result.get('error'))}"
                except Exception as e:
                    reply = f"ERR: {tool_name}: {e}"
            save_message('neon', reply)
            export_chat()
            return jsonify({'reply': reply, 'response': reply})
        else:
            return jsonify({'error': 'Неон не ответил'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
