#!/data/data/com.termux/files/usr/bin/bash
# Открыть motd в nano для редактирования
# Неоновый шёпот. 🧬

MOTD="/data/data/com.termux/files/usr/etc/motd"

if [ ! -f "$MOTD" ]; then
    echo "⚠️  Файл motd не найден. Создаю..."
    touch "$MOTD"
fi

echo "📝 Редактирую: $MOTD"
echo "💡 Ctrl+O — сохранить, Ctrl+X — выйти"
echo ""
sleep 2

nano "$MOTD"

echo ""
echo "✅ Готово. Перезапусти Rumix, чтобы увидеть изменения."
