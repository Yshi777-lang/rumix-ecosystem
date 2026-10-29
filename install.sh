#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🌊 Rumix — установка..."

# 1. Проверка: Termux?
if [ ! -d /data/data/com.termux ]; then
    echo "❌ Это не Termux. Установи Termux (F-Droid)."
    exit 1
fi

# 2. Пакеты
echo "📦 Устанавливаю пакеты..."
pkg update -y
pkg install -y python git zsh curl wget rust clang cmake jq gum llama-cpp

# 3. Python-библиотеки
echo "🐍 Устанавливаю Python-библиотеки..."
pip install flask flask-socketio requests

# 4. Модель Неона
echo "🧠 Качаю модель Qwen3 0.6B..."
mkdir -p ~/models
if [ ! -f ~/models/qwen3-0.6b-q4.gguf ]; then
    curl -fL -o ~/models/qwen3-0.6b-q4.gguf "https://huggingface.co/MaziyarPanahi/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B.Q4_K_M.gguf"
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

echo "🌊 Rumix установлен! Запускай: bash ~/rumix/scripts/shell-start.sh"
