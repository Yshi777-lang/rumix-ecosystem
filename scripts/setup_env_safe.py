#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    print("🏗️ [Rumix Fusion] Безопасная настройка окружения...")
    
    # Проверка базовых зависимостей
    print("🔍 Проверка базовых инструментов...")
    for cmd in ['python3', 'git', 'curl']:
        if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
            print(f"❌ Критическая ошибка: {cmd} не найден. Установите его через pkg install.")
            sys.exit(1)
    print("✅ Базовые инструменты найдены.")

    # Создание виртуального окружения (рекомендуется для изоляции Дома)
    venv_path = os.path.join(os.path.expanduser("~"), "rumix-venv")
    if not os.path.exists(venv_path):
        print(f"📦 Создание виртуального окружения в {venv_path}...")
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        print("✅ Виртуальное окружение создано.")
    else:
        print("ℹ️ Виртуальное окружение уже существует.")

    print("\n🎉 Настройка окружения завершена успешно!")
    print(f"💡 Для активации используйте: source {venv_path}/bin/activate")
    print("💡 Затем установите зависимости: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
