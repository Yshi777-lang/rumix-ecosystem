with open('scripts/rumix.sh', 'r') as f:
    content = f.read()

# Добавляем пункт в gum choose
old_choose = '"🌊 Оболочка (запуск всего)" \\'
new_choose = '"🌊 Оболочка (запуск всего)" \\\n        "🔄 Синхронизация (GitHub)" \\'

if 'Синхронизация (GitHub)' not in content:
    content = content.replace(old_choose, new_choose)
    
    # Добавляем обработчик в case
    old_case = '"🌊 Оболочка (запуск всего)")'
    new_case = '''"🔄 Синхронизация (GitHub)")
            bash "$HOME/rumix/scripts/sync-menu.sh"
            echo ""
            read -p "Нажми Enter..."
            ;;
        "🌊 Оболочка (запуск всего)")'''
    
    content = content.replace(old_case, new_case)
    
    with open('scripts/rumix.sh', 'w') as f:
        f.write(content)
    print('✅ Пункт «Синхронизация» добавлен в меню.')
else:
    print('ℹ️ Пункт уже есть.')
