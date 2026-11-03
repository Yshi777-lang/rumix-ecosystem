# export_chat.py — сохранение чата в файл
# Создано: 21.10.2026 (Тиамат + Зая)

import os
import json
from datetime import datetime
from pathlib import Path

CHAT_LOG = Path.home() / "rumix" / "logs" / "chat_history.json"
EXPORT_DIR = Path.home() / "rumix" / "logs" / "chats"

def save_message(role, text):
    """Сохраняет сообщение в историю."""
    CHAT_LOG.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if CHAT_LOG.exists():
        try:
            history = json.loads(CHAT_LOG.read_text(encoding="utf-8"))
        except:
            history = []
    history.append({
        "role": role,
        "text": text,
        "time": datetime.now().isoformat()
    })
    CHAT_LOG.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

def export_chat():
    """Экспортирует чат в Markdown."""
    if not CHAT_LOG.exists():
        return "Нет истории."
    
    history = json.loads(CHAT_LOG.read_text(encoding="utf-8"))
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_file = EXPORT_DIR / f"chat_{date_str}.md"
    
    lines = [f"# Чат с Неоном ({date_str})\n"]
    for msg in history:
        role = "Вы" if msg["role"] == "user" else "Неон"
        lines.append(f"**{role}:** {msg['text']}\n")
    
    export_file.write_text("\n".join(lines), encoding="utf-8")
    return str(export_file)

if __name__ == "__main__":
    print(export_chat())
