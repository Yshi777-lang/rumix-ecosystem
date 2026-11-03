#!/data/data/com.termux/files/usr/bin/bash
# sync-ecosystem.sh — синхронизация rumix -> rumix-ecosystem (без .git)

SRC="$HOME/rumix"
DST="$HOME/rumix-ecosystem"

echo "🔄 Синхронизация: $SRC -> $DST"

# 1. Копируем код (без .git, logs, __pycache__)
rsync -a --delete --exclude='.git' --exclude='logs' --exclude='__pycache__' "$SRC/" "$DST/" 2>/dev/null || {
    find "$SRC" -mindepth 1 -maxdepth 1 ! -name '.git' ! -name 'logs' -exec cp -r {} "$DST/" \;
}

# 2. Копируем карту и победы
cp "$HOME/Work/notes/CORE/RUMIX_MAP.md" "$DST/RUMIX_MAP.md" 2>/dev/null
cp "$SRC/VICTORIES.md" "$DST/VICTORIES.md" 2>/dev/null

# 3. Коммитим и пушим ТОЛЬКО в ecosystem
cd "$DST" || exit 1
git add . 2>/dev/null
if git diff --cached --quiet; then
    echo "✅ Нет изменений"
else
    git commit -m "sync: $(date +%Y-%m-%d_%H:%M)"
    git push origin main
    echo "✅ Запушено в rumix-ecosystem"
fi
