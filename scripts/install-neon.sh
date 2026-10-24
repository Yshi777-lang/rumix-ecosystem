#!/data/data/com.termux/files/usr/bin/bash
# install-neon.sh — установка Неона (локальный LLM)
# Неоновый шёпот. 🤖

echo "🤖 Установка Неона..."
echo ""

# 1. llama-cpp + runit
echo "📦 Ставлю llama-cpp и runit..."
pkg install -y llama-cpp runit 2>&1 | tail -3

# 2. Модель (из каталога models/catalog.json)
CATALOG="$HOME/rumix/models/catalog.json"
if [ ! -f "$CATALOG" ]; then
    echo "❌ Каталог моделей не найден: $CATALOG"
    exit 1
fi

# Читаем поля модели через python3
read -r MODEL_ID MODEL_FILE MODEL_URL MODEL_MIN_BYTES MODEL_SHA256 < <(python3 -c "
import json, os
c = json.load(open('$CATALOG'))
m = c['models'][0]
path = os.path.expanduser(m['local_path'])
print(m['id'], path, m['downloadUrl'], m['bytes'], m['sha256'])
")

echo "🧠 Модель: $MODEL_ID"

mkdir -p "$(dirname "$MODEL_FILE")"

# Проверка места
FREE_BYTES=$(df -k "$HOME" | awk 'NR==2 {print $4 * 1024}')
NEEDED_BYTES=$((MODEL_MIN_BYTES * 2))
if [ "$FREE_BYTES" -lt "$NEEDED_BYTES" ]; then
    echo "❌ Недостаточно места: нужно ~$((NEEDED_BYTES / 1024 / 1024)) МБ, свободно $((FREE_BYTES / 1024 / 1024)) МБ"
    exit 1
fi

# Проверка: файл есть + размер + sha256
NEED_DOWNLOAD=0
if [ ! -f "$MODEL_FILE" ]; then
    NEED_DOWNLOAD=1
else
    SIZE=$(stat -c%s "$MODEL_FILE" 2>/dev/null || echo 0)
    if [ "$SIZE" -ne "$MODEL_MIN_BYTES" ]; then
        echo "⚠️  Размер не совпадает: $SIZE ≠ $MODEL_MIN_BYTES"
        NEED_DOWNLOAD=1
    else
        echo "🔐 Проверяю SHA-256..."
        ACTUAL_SHA=$(sha256sum "$MODEL_FILE" | awk '{print $1}')
        if [ "$ACTUAL_SHA" != "$MODEL_SHA256" ]; then
            echo "❌ SHA-256 не совпадает!"
            echo "   Ожидалось: $MODEL_SHA256"
            echo "   Получено:  $ACTUAL_SHA"
            NEED_DOWNLOAD=1
            rm -f "$MODEL_FILE"
        else
            echo "✅ Модель есть, SHA-256 совпадает"
        fi
    fi
fi

if [ "$NEED_DOWNLOAD" -eq 1 ]; then
    echo "📥 Скачиваю..."
    if wget -c -O "$MODEL_FILE" "$MODEL_URL"; then
        SIZE=$(stat -c%s "$MODEL_FILE")
        if [ "$SIZE" -ne "$MODEL_MIN_BYTES" ]; then
            echo "❌ Размер не совпадает: $SIZE ≠ $MODEL_MIN_BYTES"
            rm -f "$MODEL_FILE"
            exit 1
        fi
        echo "🔐 Проверяю SHA-256..."
        ACTUAL_SHA=$(sha256sum "$MODEL_FILE" | awk '{print $1}')
        if [ "$ACTUAL_SHA" != "$MODEL_SHA256" ]; then
            echo "❌ SHA-256 не совпадает после скачивания!"
            echo "   Ожидалось: $MODEL_SHA256"
            echo "   Получено:  $ACTUAL_SHA"
            rm -f "$MODEL_FILE"
            exit 1
        fi
        echo "✅ Модель скачана и проверена: $((SIZE / 1024 / 1024)) МБ"
    else
        echo "❌ Ошибка скачивания"
        exit 1
    fi
fi

# 3. Сервис runit
echo "⚙️  Настраиваю сервис..."
mkdir -p $PREFIX/var/service/neon
cat > $PREFIX/var/service/neon/run << 'RUN_EOF'
#!/data/data/com.termux/files/usr/bin/sh
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=8
exec llama-server -m $HOME/models/qwen3-0.6b-q4.gguf -c 8192 --host 127.0.0.1 --port 8080 -fa on --chat-template-kwargs '{"enable_thinking": false}'
RUN_EOF
chmod +x $PREFIX/var/service/neon/run

# 4. Запуск
echo "🚀 Запускаю Неона..."
export SVDIR="$PREFIX/var/service"

# 4.1. Проверить runsvdir
if ! pgrep -f runsvdir >/dev/null; then
    echo "🔧 Запускаю runsvdir..."
    nohup runsvdir "$SVDIR" > "$HOME/runsvdir.log" 2>&1 &
    sleep 3
fi

# 4.2. Поднять сервис
sv up neon 2>/dev/null || true
sleep 8

# Проверка: сервер отвечает?
if curl -s --max-time 5 http://127.0.0.1:8080/v1/models | grep -q "qwen"; then
    echo "✅ Неон работает."
    echo "Проверка: curl http://127.0.0.1:8080/v1/models"
else
    echo "⚠️  Неон не отвечает. Проверь лог:"
    echo "    tail -20 $HOME/llama-test.log"
    exit 1
fi
