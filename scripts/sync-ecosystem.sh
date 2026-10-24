#!/data/data/com.termux/files/usr/bin/bash
# sync-ecosystem.sh — синхронизация rumix -> rumix-ecosystem

SRC="$HOME/rumix"
DST="$HOME/rumix-ecosystem"

echo "🔄 Синхронизация: $SRC -> $DST"

# 1. Копируем код (без .git, без logs)
rsync -av --exclude='.git' --exclude='logs' --exclude='__pycache__' "$SRC/" "$DST/" 2>/dev/null || {
    cp -r "$SRC"/* "$DST/" 2>/dev/null
    cp -r "$SRC"/.[!.]* "$DST/" 2>/dev/null
}

# 2. Копируем карту и победы
cp "$HOME/Work/notes/CORE/RUMIX_MAP.md" "$DST/RUMIX_MAP.md" 2>/dev/null
cp "$SRC/VICTORIES.md" "$DST/VICTORIES.md" 2>/dev/null

# 3. Коммитим и пушим
cd "$DST" || exit 1
git add . 2>/dev/null
if git diff --cached --quiet; then
    echo "✅ Нет изменений"
else
    git commit -m "sync: $(date +%Y-%m-%d_%H:%M)"
    git push origin main
    echo "✅ Запушено"
fi
