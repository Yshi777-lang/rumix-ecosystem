#!/data/data/com.termux/files/usr/bin/bash
# doctor.sh — «что болит у дома». Одна команда вместо шести проверок руками.
ECO_DIR="${RUMIX_ECO_DIR:-$HOME/rumix-ecosystem}"
RUMIX_DIR="${RUMIX_DATA_DIR:-$HOME/rumix}"
SHELL_URL="http://127.0.0.1:8001"
NEON_URL="http://127.0.0.1:8080"
TOKEN_FILE="$HOME/.rumix_token"

FAIL=0
WARN=0
ok() { printf '  ✅ %s\n' "$1"; }
warn() { printf '  ⚠️  %s\n' "$1"; WARN=$((WARN + 1)); }
bad() { printf '  ❌ %s\n' "$1"; FAIL=$((FAIL + 1)); }
section() { printf '\n%s\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

echo "🩺 DOCTOR RUMIX"
echo "   код: $ECO_DIR"
echo "   данные: $RUMIX_DIR"

section "1. Платформа"
if [ -d /data/data/com.termux ]; then ok "Termux на месте"; else bad "это не Termux"; fi

section "2. Python-пакеты"
if python3 -c 'import flask, flask_socketio, requests' 2>/dev/null; then ok "flask / flask-socketio / requests"; else bad "нет python-зависимостей"; fi
if python3 -c 'import termux_tts' 2>/dev/null; then ok "termux-tts (голос дома)"; else warn "нет termux_tts — голос не работает"; fi

section "3. Команды"
for cmd in curl git; do
    if have "$cmd"; then ok "$cmd"; else bad "нет $cmd"; fi
done
for cmd in jq sv termux-tts-speak termux-battery-status llama-server; do
    if have "$cmd"; then ok "$cmd"; else warn "нет $cmd"; fi
done

section "4. Сервисы"
code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "$SHELL_URL/api/agent/status" 2>/dev/null)
if [ "$code" = "200" ]; then ok "Shell (8001) отвечает"; else bad "Shell (8001) не отвечает"; fi

code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "$NEON_URL/v1/models" 2>/dev/null)
if [ "$code" = "200" ]; then ok "Неон (8080) отвечает"; else warn "Неон (8080) спит"; fi

section "5. Доступ и секреты"
if [ -f "$TOKEN_FILE" ]; then
    perms=$(stat -c %a "$TOKEN_FILE" 2>/dev/null || echo "?")
    if [ "$perms" = "600" ]; then ok "токен есть, права 600"; else warn "токен есть, но права $perms"; fi
else
    bad "нет $TOKEN_FILE — создастся при первом запуске backend/app.py"
fi

api_code=$(curl -s -o /dev/null -m 3 -w '%{http_code}' "$SHELL_URL/api/modules" 2>/dev/null)
case "$api_code" in
    401) ok "API закрыт токеном (401 без заголовка)" ;;
    200) bad "API открыт без токена" ;;
    000) warn "Shell не запущен — защиту API проверить не смог" ;;
    *) warn "неожиданный ответ API: HTTP $api_code" ;;
esac

section "6. Данные и место"
free_mb=$(df -m "$HOME" 2>/dev/null | awk 'NR==2 {print $4}')
if [ -n "${free_mb:-}" ] && [ "$free_mb" -lt 500 ] 2>/dev/null; then warn "на диске ${free_mb}MB"; else ok "диск: ${free_mb:-?}MB свободно"; fi

ram_mb=$(free -m 2>/dev/null | awk '/Mem:/ {print $7}')
if [ -n "${ram_mb:-}" ] && [ "$ram_mb" -lt 600 ] 2>/dev/null; then warn "RAM ${ram_mb}MB"; else ok "RAM: ${ram_mb:-?}MB доступно"; fi

section "7. Модули"
if [ -d "$ECO_DIR/core/modules" ]; then
    n=$(ls "$ECO_DIR"/core/modules/*.py 2>/dev/null | grep -v "__init__" | wc -l)
    ok "модулей в core/modules: $n"
else
    bad "нет core/modules"
fi

section "ИТОГ"
if [ "$FAIL" -eq 0 ]; then echo "  ✅ критичных проблем нет (предупреждений: $WARN)"; exit 0; fi
echo "  ❌ проблем: $FAIL (предупреждений: $WARN)"
exit 1
