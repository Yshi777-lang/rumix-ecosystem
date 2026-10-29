#!/data/data/com.termux/files/usr/bin/bash
echo "🌊 Полный запуск Rumix..."

# 1. Убиваем старые процессы
pkill -f "python3 app.py" 2>/dev/null
sleep 1

# 2. Запускаем Flask
cd ~/rumix/backend || exit 1
python3 app.py > ~/rumix/logs/shell.log 2>&1 &
echo "   Backend PID: $!"

# 3. Ждём, пока поднимется
sleep 3

# 4. Проверяем статус
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status | grep -q "200"; then
    echo "   ✅ Backend отвечает (200)"
else
    echo "   ❌ Backend не отвечает. Смотри логи:"
    tail -5 ~/rumix/logs/shell.log
fi

# 5. Проверяем, что страница /terminal отдаётся
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/terminal | grep -q "200"; then
    echo "   ✅ Страница /terminal доступна"
else
    echo "   ❌ Страница /terminal не отдаётся"
fi

# 6. Открываем браузер
termux-open-url http://127.0.0.1:8001/terminal
echo "   🌐 Открываю http://127.0.0.1:8001/terminal"

echo "🏁 Готово."
