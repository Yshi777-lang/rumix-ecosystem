#!/data/data/com.termux/files/usr/bin/bash
echo "🌊 Запуск Rumix и открытие терминала..."

# Убиваем старые процессы
pkill -f "python3 app.py" 2>/dev/null
sleep 1

# Запускаем Flask
cd ~/rumix/backend || exit 1
python3 app.py > ~/rumix/logs/shell.log 2>&1 &
echo "   Backend PID: $!"

# Ждём, пока поднимется
sleep 3

# Проверяем
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status | grep -q "200"; then
    echo "   ✅ Backend отвечает"
    echo "   🌐 Открываю http://127.0.0.1:8001/terminal"
    termux-open-url http://127.0.0.1:8001/terminal
else
    echo "   ❌ Backend не отвечает. Смотри логи:"
    tail -5 ~/rumix/logs/shell.log
fi
