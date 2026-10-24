with open('scripts/rumix.sh', 'r') as f:
    content = f.read()

old = 'case "$choice" in'
new = '''case "$choice" in
        "🌊 Оболочка (запуск всего)")
            bash "$HOME/rumix/scripts/launch-all.sh"
            echo ""
            read -p "Нажми Enter..."
            ;;'''

if 'Оболочка (запуск всего)' not in content.split('case "$choice" in')[1]:
    content = content.replace(old, new)
    with open('scripts/rumix.sh', 'w') as f:
        f.write(content)
    print('✅ Обработчик «Оболочка» добавлен в case.')
else:
    print('ℹ️ Обработчик уже есть.')
