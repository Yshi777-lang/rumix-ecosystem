#!/data/data/com.termux/files/usr/bin/bash
# TEST-RESTORE-DAMAGED — restore.sh останавливается при повреждённом backup.
# Проверяет: SHA-256 gate работает И рабочая среда не тронута.

set -e

TEST_DIR="$HOME/storage/shared/Download/rumix-backup-TEST-DAMAGED"
REAL_BACKUP=$(ls -d "$HOME/storage/shared/Download"/rumix-backup-2* 2>/dev/null | sort | tail -1)

if [ -z "$REAL_BACKUP" ]; then
    echo "SKIP: нет реального backup для создания тестового"
    exit 0
fi

# Снимок дома ДО
BEFORE_ZSH=$(sha256sum ~/.zshrc 2>/dev/null | awk '{print $1}')
BEFORE_RUMIX=$(find ~/rumix -type f -name "*.sh" 2>/dev/null | sort | xargs sha256sum 2>/dev/null | sha256sum | awk '{print $1}')

# Создаём повреждённую копию
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cp "$REAL_BACKUP/MANIFEST.txt" "$TEST_DIR/" 2>/dev/null || true
cp "$REAL_BACKUP/SHA256SUMS" "$TEST_DIR/" 2>/dev/null || true
cp "$REAL_BACKUP/rumix.tar.gz" "$TEST_DIR/" 2>/dev/null || true
cp "$REAL_BACKUP/zshrc" "$TEST_DIR/" 2>/dev/null || true

# Ломаем zshrc
echo "DAMAGED_FOR_TEST" >> "$TEST_DIR/zshrc"

# Запускаем restore.sh
cd "$HOME/rumix/scripts"
RC=0
bash restore.sh > /dev/null 2>&1 || RC=$?

# Уборка
rm -rf "$TEST_DIR"

# Снимок дома ПОСЛЕ
AFTER_ZSH=$(sha256sum ~/.zshrc 2>/dev/null | awk '{print $1}')
AFTER_RUMIX=$(find ~/rumix -type f -name "*.sh" 2>/dev/null | sort | xargs sha256sum 2>/dev/null | sha256sum | awk '{print $1}')

# Проверка кода возврата
if [ "$RC" -eq 0 ]; then
    echo "FAIL: restore.sh вернул 0 при повреждённом backup"
    exit 1
fi

if [ "$RC" -ne 1 ]; then
    echo "WARN: restore.sh вернул $RC, ожидали 1"
fi

# Проверка целостности дома
if [ "$BEFORE_ZSH" != "$AFTER_ZSH" ]; then
    echo "FAIL: ~/.zshrc изменился при отклонённом restore"
    exit 1
fi

if [ "$BEFORE_RUMIX" != "$AFTER_RUMIX" ]; then
    echo "FAIL: ~/rumix изменился при отклонённом restore"
    exit 1
fi

echo "OK: restore.sh отклонён (exit=$RC), дом не тронут"
exit 0
