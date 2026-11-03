#!/data/data/com.termux/files/usr/bin/bash
# start-all.sh — поднять весь дом через tmux (Android не убивает)

echo "🔓 Wakelock..."
termux-wake-lock

# Убиваем старые сессии (если есть)
tmux kill-session -t neon 2>/dev/null
tmux kill-session -t shell 2>/dev/null
tmux kill-session -t scanner 2>/dev/null

echo "🧠 Запуск Неона (tmux: neon)..."
tmux new-session -d -s neon "cd ~/rumix/scripts && bash neon.sh start; bash"

echo "🌐 Запуск Shell (tmux: shell)..."
tmux new-session -d -s shell "cd ~/rumix/backend && python3 app.py"

echo "🛡️ Запуск CyberScanner (tmux: scanner)..."
tmux new-session -d -s scanner "cd ~/Work/archive/CyberScanner-v2/web && python3 app.py"

echo "⏳ Ждём 5 сек..."
sleep 5

echo "📊 Проверка..."
tmux ls
echo ""
curl -s -o /dev/null -w "   Shell: %{http_code}\n" http://127.0.0.1:8001/
curl -s -o /dev/null -w "   Scanner: %{http_code}\n" http://127.0.0.1:8002/

echo "🏁 Дом запущен (tmux: neon, shell, scanner)."
