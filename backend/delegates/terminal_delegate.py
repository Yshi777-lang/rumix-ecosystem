# terminal_delegate.py — маршрут для веб-терминала
# Создано: 18.10.2026 (Тиамат + Зая)

from flask import Blueprint, request, jsonify
from web.terminal_api import run_command

terminal_bp = Blueprint('terminal', __name__)

@terminal_bp.route('/api/terminal', methods=['POST'])
def api_terminal():
    data = request.get_json()
    cmd = data.get('cmd', '')
    consent = data.get('consent', False)
    if not cmd:
        return jsonify({'status': 'ERROR', 'message': 'Пустая команда.'}), 400
    return jsonify(run_command(cmd, user_consent=consent))
