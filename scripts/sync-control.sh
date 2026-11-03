#!/data/data/com.termux/files/usr/bin/bash
# sync-control.sh — управление синхронизацией Work с GitHub
# Создано: 21.10.2026 (Тиамат + Зая)

case "$1" in
    start)
        # Добавляем cron-задание, если его нет
        (crontab -l 2>/dev/null | grep -v "sync-all-bg.sh"; echo "*/15 * * * * bash ~/rumix/scripts/sync-all-bg.sh") | crontab -
        echo "✅ Синхронизация запущена (каждые 15 минут)."
        ;;
    stop)
        # Удаляем cron-задание
        (crontab -l 2>/dev/null | grep -v "sync-all-bg.sh") | crontab -
        echo "⏹ Синхронизация остановлена."
        ;;
    interval)
        if [ -z "$2" ]; then
            echo "❌ Укажи интервал в минутах: bash sync-control.sh interval 30"
            exit 1
        fi
        # Меняем интервал
        (crontab -l 2>/dev/null | grep -v "sync-all-bg.sh"; echo "*/$2 * * * * bash ~/rumix/scripts/sync-all-bg.sh") | crontab -
        echo "✅ Интервал изменён на $2 минут."
        ;;
    status)
        if crontab -l 2>/dev/null | grep -q "sync-all-bg.sh"; then
            interval=$(crontab -l 2>/dev/null | grep "sync-all-bg.sh" | awk '{print $1}' | sed 's|*/||;s| ||g')
            echo "🔄 Синхронизация работает каждые $interval минут."
        else
            echo "⏹ Синхронизация остановлена."
        fi
        ;;
    now)
        bash ~/rumix/scripts/sync-all-bg.sh
        ;;
    *)
        echo "Использование:"
        echo "  bash sync-control.sh start      — запустить"
        echo "  bash sync-control.sh stop       — остановить"
        echo "  bash sync-control.sh interval N — изменить интервал (минут)"
        echo "  bash sync-control.sh status     — статус"
        echo "  bash sync-control.sh now        — синхронизировать сейчас"
        ;;
esac
