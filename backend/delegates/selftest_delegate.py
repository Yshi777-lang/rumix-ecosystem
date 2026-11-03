# selftest_delegate.py — маршрут для диагностики
# Создано: 18.10.2026 (Тиамат + Зая)

from flask import Blueprint, jsonify
from backend.selftest import run_all

selftest_bp = Blueprint('selftest', __name__)

@selftest_bp.route('/api/selftest', methods=['GET'])
def api_selftest():
    return jsonify(run_all())
