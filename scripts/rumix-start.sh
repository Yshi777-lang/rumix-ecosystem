#!/data/data/com.termux/files/usr/bin/bash
# rumix-start.sh — поднять сервер и открыть браузер
# Создано: 19.10.2026 (Тиамат + Зая)

echo "🌊 Rumix — запуск..."

# Останавливаем старый сервер
pkill -f "python3 app.py" 2>/dev/null

# Запускаем Flask
cd ~/rumix/backend || exit 1
python3 app.py > ~/rumix/logs/shell.log 2>&1 &
echo "   Backend PID: $!"

# Ждём
sleep 2

# Проверяем
if curl -s http://127.0.0.1:8001/api/status > /dev/null; then
    echo "   ✅ Backend отвечает"
    echo "   🌐 Открываю http://127.0.0.1:8001"
    termux-open-url http://127.0.0.1:8001
else
    echo "   ❌ Backend не отвечает. Смотри логи: ~/rumix/logs/shell.log"
fi
