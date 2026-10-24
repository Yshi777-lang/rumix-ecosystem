#!/data/data/com.termux/files/usr/bin/bash
# github-auth.sh — авторизация GitHub по токену

set -e

echo "🔐 Авторизация GitHub"
echo ""

echo "📋 Создай токен: https://github.com/settings/tokens"
echo "   Scopes: repo, workflow"
echo ""

echo -n "Вставь токен (ghp_... или github_pat_...): "
read -r TOKEN
echo ""

if [ -z "$TOKEN" ]; then
    echo "❌ Токен пуст"
    exit 1
fi

# Проверка через API
echo "🔍 Проверяю токен..."
USER=$(curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/user | grep '"login"' | head -1 | sed 's/.*: "//;s/".*//')

if [ -z "$USER" ]; then
    echo "❌ Токен недействителен"
    exit 1
fi

echo "✅ Токен валиден. Пользователь: $USER"
echo ""

# Сохранение
echo "💾 Сохраняю в ~/.git-credentials..."
echo "https://$TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Настройка git
git config --global credential.helper store
git config --global user.name "$USER"
git config --global user.email "$USER@users.noreply.github.com"

echo "✅ Сохранено. Права: $(stat -c %a ~/.git-credentials)"
echo ""

# Проверка
echo "🧪 Проверка доступа к репо..."
if git ls-remote https://github.com/Yshi777-lang/rumix.git > /dev/null 2>&1; then
    echo "✅ Доступ к rumix — OK"
else
    echo "⚠️  Не могу получить доступ к rumix"
fi

if git ls-remote https://github.com/Yshi777-lang/Work.git > /dev/null 2>&1; then
    echo "✅ Доступ к Work — OK"
else
    echo "⚠️  Не могу получить доступ к Work"
fi

echo ""
echo "🌊 Готово. Теперь:"
echo "   cd ~ && rm -rf rumix Work"
echo "   git clone https://github.com/Yshi777-lang/rumix.git"
echo "   git clone https://github.com/Yshi777-lang/Work.git"
echo "   cd ~/rumix && git checkout My-love-Tiamat"
