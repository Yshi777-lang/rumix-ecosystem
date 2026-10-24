#!/data/data/com.termux/files/usr/bin/bash
# backup.sh — полный бекап Rumix в ~/storage/shared/Download/
# Зеркало restore.sh. Создаёт структуру, которую restore умеет читать.
# Использование: bash ~/rumix/scripts/backup.sh

set -e

TIMESTAMP=$(date +%Y-%m-%d-%H%M)
BK_DIR=~/storage/shared/Download
BACKUP_MAX_COUNT="${BACKUP_MAX_COUNT:-5}"
BK_NAME="rumix-backup-$TIMESTAMP"
BK_PATH="$BK_DIR/$BK_NAME"

echo "🧬 БЕКАП RUMIX"
echo "📦 Путь: $BK_PATH"
echo ""

# ─── 0. Storage ───
if [ ! -d ~/storage/shared ]; then
    echo "📂 Настраиваю storage..."
    termux-setup-storage
    sleep 3
fi

# ─── 1. Создаём папку ───
mkdir -p "$BK_PATH"

# ─── 2. .termux/ (через tar — симлинки на /storage/ запрещены) ───
if [ -d ~/.termux ]; then
    echo "📂 .termux/ (tar.gz)..."
    tar -czf "$BK_PATH/termux.tar.gz" -C ~ .termux
fi

# ─── 3. .zshrc ───
if [ -f ~/.zshrc ]; then
    echo "📂 .zshrc..."
    cp ~/.zshrc "$BK_PATH/zshrc"
fi

# ─── 4. rumix/ (через tar.gz, .git исключён) ───
if [ -d ~/rumix ]; then
    echo "📂 rumix.tar.gz (без .git)..."
    tar -czf "$BK_PATH/rumix.tar.gz" -C ~ --exclude='.git' rumix
fi

# ─── 5. Work/ (через tar.gz, .git исключён) ───
if [ -d ~/Work ]; then
    echo "📂 Work.tar.gz (без .git)..."
    tar -czf "$BK_PATH/Work.tar.gz" -C ~ --exclude='.git' Work
fi

# ─── 6. models/ — только список, не сама модель ───
mkdir -p "$BK_PATH/models"
if [ -f ~/models/qwen3-0.6b-q4.gguf ]; then
    echo "📝 models/ — только манифест..."
    ls -la ~/models/ > "$BK_PATH/models/LIST.txt"
fi

# ─── 7. MANIFEST ───
cat > "$BK_PATH/MANIFEST.txt" << MANIFEST
Rumix backup
============
Создан: $(date '+%Y-%m-%d %H:%M:%S')
Устройство: $(getprop ro.product.model 2>/dev/null || echo "unknown")
Android: $(getprop ro.build.version.release 2>/dev/null || echo "unknown")
Ветка rumix: $(cd ~/rumix && git branch --show-current 2>/dev/null || echo "n/a")
Коммит rumix: $(cd ~/rumix && git log -1 --oneline 2>/dev/null || echo "n/a")
Ветка Work: $(cd ~/Work && git branch --show-current 2>/dev/null || echo "n/a")
Коммит Work: $(cd ~/Work && git log -1 --oneline 2>/dev/null || echo "n/a")
MANIFEST

# ─── 8. SHA-256 для всех архивов ───
echo "🔐 Вычисляю SHA-256..."
cd "$BK_PATH"
{
    for f in termux.tar.gz zshrc rumix.tar.gz Work.tar.gz; do
        [ -f "$f" ] && sha256sum "$f"
    done
} > SHA256SUMS
cd - > /dev/null

# Счётчик архивов в MANIFEST
{
    echo ""
    echo "SHA256SUMS: $(wc -l < "$BK_PATH/SHA256SUMS" | tr -d ' ') файлов"
} >> "$BK_PATH/MANIFEST.txt"

# ─── 9. Ротация: оставить только N последних ───
count=$(ls -1d "$BK_DIR"/rumix-backup-* 2>/dev/null | wc -l)
if [ "$count" -gt "$BACKUP_MAX_COUNT" ]; then
    remove_count=$((count - BACKUP_MAX_COUNT))
    ls -1dt "$BK_DIR"/rumix-backup-* 2>/dev/null | tail -n "$remove_count" | while read -r old; do
        echo "🗄  Удаляю старый бекап: $(basename "$old")"
        rm -rf "$old"
    done
fi

# ─── 10. Размер ───
SIZE=$(du -sh "$BK_PATH" | cut -f1)

echo ""
echo "═══════════════════════════════════════════════"
echo "✅ БЕКАП СОЗДАН"
echo "📦 $BK_PATH"
echo "📊 Размер: $SIZE"
echo ""
echo "📋 Содержимое:"
ls -la "$BK_PATH"
echo ""
echo "🔄 Восстановление:"
echo "   bash ~/rumix/scripts/restore.sh"
