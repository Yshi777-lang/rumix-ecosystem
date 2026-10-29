#!/data/data/com.termux/files/usr/bin/bash
# status.sh — быстрый статус дома

echo "═══════════════════════════════════════"
echo "📊 СТАТУС ДОМА"
echo "═══════════════════════════════════════"

check_port() {
  local name=$1 port=$2
  if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$port 2>/dev/null | grep -q "200\|404\|302"; then
    echo "  ✅ $name (порт $port) — жив"
  else
    echo "  ❌ $name (порт $port) — спит"
  fi
}

check_port "Shell" 8001
check_port "Неон" 8080
check_port "Сканер" 8002

echo "───────────────────────────────────────"
df -h ~/ | tail -1 | awk "{print \"  💾 Диск: \" \$4 \" свободно\"}"
free -h | grep Mem | awk "{print \"  🧠 Память: \" \$3 \" / \" \$2}"
echo "═══════════════════════════════════════"
