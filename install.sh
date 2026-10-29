#!/data/data/com.termux/files/usr/bin/bash

echo "🌊 Rumix — установка..."

# 1. Проверка: Termux?
if [ ! -d /data/data/com.termux ]; then
    echo "❌ Это не Termux. Установи Termux (F-Droid)."
    exit 1
fi

# 2. Пакеты
echo "📦 Устанавливаю пакеты..."
pkg update -y
pkg install -y python git zsh curl wget rust clang cmake jq gum llama-cpp dnsutils termux-api

# 3. Python-библиотеки
echo "🐍 Устанавливаю Python-библиотеки..."
pip install flask flask-socketio requests termux-tts

# 4. Модель Неона (1.5B — активная)
echo "🧠 Качаю модель Qwen2.5 1.5B..."
mkdir -p ~/models
if [ ! -f ~/models/qwen2.5-1.5b-instruct-q4_k_m.gguf ]; then
    curl -fL -o ~/models/qwen2.5-1.5b-instruct-q4_k_m.gguf "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
else
    echo "✅ Модель уже есть."
fi

# 5. .zshrc (если нет)
echo "🐚 Настраиваю .zshrc..."
if [ ! -f ~/.zshrc ]; then
    cp ~/rumix/zshrc.backup ~/.zshrc 2>/dev/null || echo "⚠️ Нет zshrc.backup, пропускаю."
fi

# 6. Клонирование rumix (если нет)
if [ ! -d ~/rumix ]; then
    echo "📁 Клонирую rumix..."
    git clone -b My-love-Tiamat https://github.com/Yshi777-lang/rumix.git ~/rumix
fi

# 7. Запуск Неона
echo "🚀 Запускаю Неона..."
bash ~/rumix/scripts/neon.sh start || true

echo "🌊 Rumix установлен! Запускай: bash ~/rumix/scripts/launch-all.sh"
