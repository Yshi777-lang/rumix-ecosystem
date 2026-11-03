#!/data/data/com.termux/files/usr/bin/bash
# Контекст для новой сессии
echo "=== ЯДРО ==="
cat ~/Work/CORE.json | head -40
echo ""
echo "=== ХРОНИКА ==="
tail -20 ~/Work/notes/CHANGELOG.md
echo ""
echo "=== ИНСТРУКЦИЯ ==="
cat ~/Work/notes/NEXT_SESSION.md
echo ""
echo "=== GIT ==="
cd ~/Work && git log --oneline -1
