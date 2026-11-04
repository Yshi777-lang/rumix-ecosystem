#!/data/data/com.termux/files/usr/bin/bash
# shell-start.sh — запуск Rumix Shell
# Исправлено: 21.10.2026 (задержка + повторные проверки)

echo "🌊 Rumix Shell — запуск..."
ECO_DIR="$HOME/rumix-ecosystem"

# Убиваем старый процесс
pkill -f "python3 app.py" 2>/dev/null
sleep 1

# Переходим в папку бэкенда
# Запускаем из rumix-ecosystem, если он есть, иначе из rumix
if [ -d "$ECO_DIR/backend" ]; then
    cd "$ECO_DIR/backend" || exit 1
else
    cd ~/rumix-ecosystem/backend || exit 1
fi

# Запускаем Flask в фоне
python3 app.py > ~/rumix/logs/shell.log 2>&1 &
PID=$!
echo "   Backend PID: $PID"

# Ждём до 10 секунд (5 попыток по 2 сек)
OK=0
for i in 1 2 3 4 5; do
    sleep 2
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status | grep -q "200"; then
        OK=1
        break
    fi
done

if [ $OK -eq 1 ]; then
    echo "   ✅ Backend отвечает"
    echo "   🌐 Открываю http://127.0.0.1:8001"
    termux-open-url http://127.0.0.1:8001
else
    echo "   ❌ Backend не отвечает. Смотри логи: ~/rumix/logs/shell.log"
fi
