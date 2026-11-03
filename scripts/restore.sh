#!/data/data/com.termux/files/usr/bin/bash
# restore.sh — восстановление из бекапа
# Создано: 21.10.2026 (Тиамат + Зая)

BACKUP_DIR="$HOME/storage/shared/Download"

# Ищем последний бекап
LATEST=$(ls -td "$BACKUP_DIR"/rumix-backup-* 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    echo "❌ Бекапы не найдены в $BACKUP_DIR"
    exit 1
fi

echo "🔄 Восстановление из: $LATEST"

# ─── Проверка SHA-256 ───
if [ -f "$LATEST/SHA256SUMS" ]; then
    echo "🔐 Проверяю целостность архивов..."
    cd "$LATEST"
    if sha256sum -c SHA256SUMS --quiet 2>/dev/null; then
        echo "✅ Все архивы целы."
    else
        echo "❌ Ошибка: архивы повреждены. Восстановление отменено."
        exit 1
    fi
    cd - > /dev/null
else
    echo "⚠️ Файл SHA256SUMS не найден. Пропускаю проверку."
fi

# Распаковываем rumix
if [ -f "$LATEST/rumix.tar.gz" ]; then
    tar -xzf "$LATEST/rumix.tar.gz" -C ~/
    echo "✅ rumix восстановлен."
fi

# Распаковываем Work (если есть)
if [ -f "$LATEST/Work.tar.gz" ]; then
    tar -xzf "$LATEST/Work.tar.gz" -C ~/
    echo "✅ Work восстановлен."
fi

# Распаковываем termux
if [ -f "$LATEST/termux.tar.gz" ]; then
    tar -xzf "$LATEST/termux.tar.gz" -C ~/
    echo "✅ termux восстановлен."
fi

# zshrc
if [ -f "$LATEST/zshrc" ]; then
    cp "$LATEST/zshrc" ~/.zshrc
    echo "✅ zshrc восстановлен."
fi

echo "🏁 Восстановление завершено."
