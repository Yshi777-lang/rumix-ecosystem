#!/data/data/com.termux/files/usr/bin/bash
# sync-all.sh — синхронизация всех репозиториев: Work, rumix, rumix-ecosystem

echo "🔄 Синхронизация всех репозиториев..."

# 1. Work (душа)
cd ~/Work || exit 1
git add -A
if ! git diff --cached --quiet; then
    git commit -m "Auto-sync Work: $(date +'%Y-%m-%d %H:%M')"
fi
git pull --rebase origin main && git push origin main
echo "✅ Work синхронизирован"

# 2. rumix (тело)
cd ~/rumix || exit 1
git add -A
if ! git diff --cached --quiet; then
    git commit -m "Auto-sync rumix: $(date +'%Y-%m-%d %H:%M')"
fi
git pull --rebase origin My-love-Tiamat && git push origin My-love-Tiamat
echo "✅ rumix синхронизирован"

# 3. rumix-ecosystem (экосистема)
cd ~/rumix-ecosystem || exit 1
# Копируем код из rumix (без .git)
rsync -a --exclude='.git' --exclude='logs' --exclude='__pycache__' ~/rumix/ ~/rumix-ecosystem/ 2>/dev/null
git add -A
if ! git diff --cached --quiet; then
    git commit -m "Auto-sync ecosystem: $(date +'%Y-%m-%d %H:%M')"
fi
git pull --rebase origin main && git push origin main
echo "✅ rumix-ecosystem синхронизирован"

echo "🎉 Все репозитории синхронизированы!"
