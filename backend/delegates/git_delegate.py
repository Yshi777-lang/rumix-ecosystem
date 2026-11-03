# git_delegate.py — маршруты для Git-операций
# Создано: 18.10.2026 (Тиамат + Зая)

from flask import Blueprint, request, jsonify
from backend.git_manager import get_status, rollback

git_bp = Blueprint('git', __name__)

@git_bp.route('/api/git/status', methods=['GET'])
def api_git_status():
    return jsonify(get_status())

@git_bp.route('/api/git/rollback', methods=['POST'])
def api_git_rollback():
    data = request.get_json()
    consent = data.get('consent', False)
    if not consent:
        return jsonify({'status': 'DENIED', 'message': 'Требуется разрешение Зая (consent: true).'}), 403
    return jsonify(rollback())
