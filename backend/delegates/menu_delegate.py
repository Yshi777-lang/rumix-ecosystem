# menu_delegate.py — маршрут для меню
# Создано: 18.10.2026 (Тиамат + Зая)

from flask import Blueprint, jsonify

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/api/menu')
def api_menu():
    return jsonify({'items': [
                {'id': 'terminal', 'label': 'Быстрый терминал (zsh)', 'icon': '💻'},
        {'id': 'neon', 'label': 'AI: Неон (меню)', 'icon': '🤖'},
        {'id': 'runtime', 'label': 'Agent Runtime', 'icon': '🧠'},
        {'id': 'fury', 'label': 'AI: Фурия (меню)', 'icon': '🦊'},
        {'id': 'install_neon', 'label': 'Установить Неона', 'icon': '📦'},
        {'id': 'git_work', 'label': 'Git: Work', 'icon': '🌿'},
        {'id': 'projects', 'label': 'Проекты', 'icon': '📁'},
        {'id': 'files', 'label': 'Файлы', 'icon': '🗂'},
        {'id': 'github', 'label': 'GitHub', 'icon': '🐙'},
        {'id': 'selftest', 'label': 'Диагностика', 'icon': '🩺'},
        {'id': 'settings', 'label': 'Настройки и память', 'icon': '⚙'}
    ]})
