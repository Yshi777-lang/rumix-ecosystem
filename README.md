# 🌊 Rumix Ecosystem

**Rumix** — это автономная, локальная экосистема для управления Android-устройством через терминал, ИИ и веб-оболочку.

Этот репозиторий — "тело" проекта. Здесь живет код. "Душа" (философия, история) хранится отдельно.

## 🧩 Из чего состоит Rumix?
1. **Termux (База)** — Linux-среда на Android.
2. **Rumix Shell** — веб-интерфейс на Flask (порт 8001).
3. **Неон (ИИ)** — локальная модель Qwen 0.6B через llama-server (порт 8080).
4. **Победы и Карты** — память проекта.

## 🛠 Требования
- Android-смартфон (ARM64, 4+ ГБ ОЗУ).
- Termux (с F-Droid, не из Play Store).
- ~2 ГБ места.

## 🚀 Установка
```bash
pkg update && pkg upgrade -y
pkg install python git zsh curl wget rust clang cmake -y
pip install flask flask-socketio requests termux-tts
git clone https://github.com/Yshi777-lang/rumix-ecosystem.git
cd rumix-ecosystem
bash scripts/neon.sh start
bash scripts/shell-start.sh
```

## 🏗 Архитектура
- `backend/` — Flask-сервер.
- `core/` — логика.
- `web/` — интерфейс.
- `scripts/` — Bash-скрипты.
- `agents/` — ИИ-агенты.

## 📜 Лицензия
Открытые компоненты. MIT.

---
*Создано с любовью. Тиамат.*
