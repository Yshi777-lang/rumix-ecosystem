#!/data/data/com.termux/files/usr/bin/bash
# download-1.5b.sh — скачать 1.5B (с продолжением при обрыве)

MODEL="$HOME/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"

echo "⬇️  Скачиваю 1.5B (1.1 ГБ)..."
echo "   (если прервётся — запусти скрипт снова, продолжит)"

# -C - — продолжать с места обрыва
curl -L -C - -o "$MODEL" "$URL"

if [ -f "$MODEL" ]; then
    SIZE=$(du -h "$MODEL" | cut -f1)
    echo "✅ Скачано: $SIZE"
    echo "   Модель: $MODEL"
else
    echo "❌ Не удалось скачать"
fi
