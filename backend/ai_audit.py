#!/usr/bin/env python3
import sys
import re
import argparse

# База знаний для локального анализа (в будущем заменяется на LLM API call)
ERROR_PATTERNS = {
    r"Permission denied": "🚨 Ошибка прав доступа. Решение: 1) Проверь `chmod +x <файл>`. 2) В Termux файлы вне `$PREFIX` (например, в `/sdcard`) не могут быть исполняемыми из-за W^X. Скопируй файл в `$HOME` или используй `sdcard-exec`.",
    r"ModuleNotFoundError|No module named": "🐍 Не найден модуль Python. Решение: 1) Проверь опечатку в имени. 2) Установи модуль: `pip install <имя_модуля>`. 3) Проверь виртуальное окружение (`venv`).",
    r"SyntaxError: invalid syntax": "📝 Синтаксическая ошибка. Решение: Проверь строку, указанную в ошибке. Частые причины: пропущенные двоеточия, неправильные отступы, незакрытые кавычки или скобки.",
    r"command not found": "❓ Команда не найдена. Решение: 1) Проверь опечатку. 2) Убедись, что пакет установлен (`pkg install <имя>`). 3) Проверь переменную `$PATH`.",
    r"Function not implemented|ENOSYS": "⚙️ Ошибка уровня ядра (часто в proot). Решение: Система заблокировала системный вызов. Попробуй использовать альтернативу без ptrace или обнови termux-exec."
}

def analyze_error(text):
    print("\n🔍 [AI-Анализ] Ищу знакомые паттерны ошибок...\n" + "-"*50)
    found = False
    for pattern, solution in ERROR_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            print(f"✅ Найдено совпадение:\n{solution}")
            found = True
    if not found:
        print("⚠️ Специфичный паттерн не найден в локальной базе.\n💡 Рекомендация: Скопируй эту ошибку в веб-поиск или используй флаг --api (при наличии ключа) для глубокого анализа LLM.")
    print("-" * 50)

def explain_command(cmd):
    print(f"\n📖 [AI-Объяснение] для команды: '{cmd}'\n" + "-"*50)
    explanations = {
        "chmod": "Изменяет права доступа к файлу. `+x` делает файл исполняемым.",
        "grep": "Ищет строки в файлах, соответствующие регулярному выражению.",
        "pkg install": "Менеджер пакетов Termux (обертка над apt) для установки ПО.",
        "proot": "Эмулятор пользовательского пространства, позволяющий запускать Linux-дистрибутивы без root.",
        "termux-wake-lock": "Запрещает Android усыплять процессор, пока Termux активен."
    }
    
    base_cmd = cmd.split()[0] if cmd else ""
    if base_cmd in explanations:
        print(f"ℹ️ {explanations[base_cmd]}")
    else:
        print(f"ℹ️ Базовая команда '{base_cmd}'. Используй `man {base_cmd}` для полной справки или подключи LLM API для детального разбора.")
    print("-" * 50)

def refactor_code(code):
    print("\n🛠️ [AI-Рефакторинг] Применяю базовые best practices...\n" + "-"*50)
    lines = code.split('\n')
    refactored = []
    
    # 1. Добавляем shebang, если это bash/python и его нет
    if lines and not lines[0].startswith('#!'):
        if 'python' in code.lower() or '.py' in code:
            refactored.append('#!/usr/bin/env python3')
        else:
            refactored.append('#!/bin/bash\nset -euo pipefail')
            
    refactored.extend(lines)
    
    # 2. Убираем лишние пустые строки в конце
    while refactored and refactored[-1].strip() == '':
        refactored.pop()
        
    print('\n'.join(refactored))
    print("-" * 50 + "\n✅ Рефакторинг завершен (локальные эвристики).")



def analyze_rumix_logs(log_text: str) -> str:
    """
    Специализированный анализатор логов для модуля "Фурия" и системного аудита Дома.
    Ищет специфичные паттерны ошибок Rumix Ecosystem.
    """
    rumix_patterns = {
        r"Out of memory|OOM|Killed": "🚨 Критическая ошибка: Нехватка памяти (OOM). Решение: 1) Проверь запущенные тяжелые процессы (neon, rag). 2) Используй process-monitor. 3) Уменьши контекст LLM или используй swap.",
        r"llama\.cpp|segmentation fault": "🧠 Ошибка локального ИИ (llama-cpp). Решение: 1) Проверь совместимость модели с CPU. 2) Уменьши количество потоков (-t). 3) Проверь доступную RAM.",
        r"Address already in use|port 8001": "🔌 Порт 8001 уже занят. Решение: Выполни 'bash scripts/shell-stop.sh' или найди процесс: 'lsof -i :8001' и заверши его.",
        r"Permission denied.*DATA_HOME|HOME": "🛡️ Сработала защита песочницы или прав доступа. Убедись, что операция разрешена в file_gate.py и пути корректны."
    }
    
    print("\n🔍 [AI-Аудит Дома] Анализ логов Rumix...\n" + "-"*50)
    found = False
    for pattern, solution in rumix_patterns.items():
        if re.search(pattern, log_text, re.IGNORECASE):
            print(f"✅ Найдено совпадение:\n{solution}")
            found = True
            
    if not found:
        print("ℹ️ Специфичных ошибок Rumix не найдено. Применяем общий анализ...")
        print("💡 Рекомендация: Проверь целостность системы через модуль 'Аудит' или 'Целостность' в веб-интерфейсе.")
        
    print("-" * 50)
    return "Анализ завершен."

def main():
    parser = argparse.ArgumentParser(description="AI CLI-ассистент для Termux (v3.0 Concept)")
    parser.add_argument('action', choices=['analyze', 'explain', 'refactor', 'audit_rumix'], help="Действие")
    parser.add_argument('target', nargs='?', default='', help="Текст ошибки, команда или код для обработки")
    
    args = parser.parse_args()
    
    if not args.target:
        print("❌ Ошибка: укажите целевой текст. Пример: ai_assist analyze 'Permission denied'")
        sys.exit(1)
        
    if args.action == 'analyze':
        analyze_error(args.target)
    elif args.action == 'explain':
        explain_command(args.target)
    elif args.action == 'refactor':
        refactor_code(args.target)
    elif args.action == 'audit_rumix':
        analyze_rumix_logs(args.target)

if __name__ == '__main__':
    main()
