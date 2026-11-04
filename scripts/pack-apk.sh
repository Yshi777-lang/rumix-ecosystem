#!/data/data/com.termux/files/usr/bin/bash
# pack-apk.sh — упаковка папки apk в ZIP для сборки в облаке.

SRC="$HOME/rumix-ecosystem/apk"
DEST="$HOME/storage/shared/Download/apk-build-$(date +%Y%m%d_%H%M).zip"
TMP="$HOME/tmp-pack-apk"

if [ ! -d "$SRC" ]; then
    echo "❌ Папка apk не найдена: $SRC"
    exit 1
fi

echo "📦 Упаковываю apk в ZIP..."

# 1. Чистим и создаём временную папку
rm -rf "$TMP"
mkdir -p "$TMP"

# 2. Копируем apk без мусора
# Используем tar для копирования (быстро и с исключениями)
(cd "$HOME/rumix-ecosystem" && tar -cf - --exclude='.git' --exclude='build' --exclude='.gradle' --exclude='*.apk' apk) | (cd "$TMP" && tar -xf -)

# 3. Упаковываем в ZIP из временной папки
cd "$TMP" && zip -r -q "$DEST" apk

# 4. Чистим временную папку
cd ~
rm -rf "$TMP"

if [ -f "$DEST" ]; then
    SIZE=$(du -h "$DEST" | cut -f1)
    echo "✅ Архив создан: $DEST ($SIZE)"
else
    echo "❌ Ошибка создания архива."
fi
