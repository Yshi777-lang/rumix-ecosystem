with open('scripts/rumix.sh', 'r') as f:
    content = f.read()

# Ищем блок gum choose
old = 'choice=$(gum choose --height 20 \\\n        "💻 Terminal (zsh)" \\'
new = 'choice=$(gum choose --height 20 \\\n        "🌊 Оболочка (запуск всего)" \\\n        "💻 Terminal (zsh)" \\'

if old in content:
    content = content.replace(old, new)
    with open('scripts/rumix.sh', 'w') as f:
        f.write(content)
    print('✅ Пункт «Оболочка» добавлен первым.')
else:
    print('❌ Блок не найден. Проверь вручную.')
