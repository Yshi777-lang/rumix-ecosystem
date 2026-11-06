import os
import re
from flask import Flask, request, jsonify, session, render_template

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-rumix-key-change-me")

# Правка 6: Строгая проверка Origin, а не по подстроке
ALLOWED_ORIGINS = {'http://127.0.0.1:8001', 'http://127.0.0.1:5001', 'http://localhost:8001'}

@app.before_request
def check_local_origin():
    if request.method in ['POST', 'PUT', 'DELETE']:
        origin = request.headers.get('Origin')
        if origin and origin not in ALLOWED_ORIGINS:
            return jsonify({"error": "Unauthorized origin"}), 403

# Правка 4: Безопасный режим отладки (по умолчанию ВЫКЛ, нет RCE)
is_debug = os.environ.get('FLASK_DEBUG', '0') == '1'

def get_db_connection():
    import sqlite3
    return sqlite3.connect('forge.db')

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            raw_content TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            type TEXT,
            content TEXT,
            FOREIGN KEY (prompt_id) REFERENCES prompts (id)
        )
    ''')
    conn.commit()
    conn.close()

# Инициализируем БД при старте
init_db()


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    # Правка 1: Добавлен raw_content в выборку
    conn = get_db_connection()
    prompts = conn.execute(
        'SELECT id, title, raw_content, status, created_at FROM prompts ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(p) for p in prompts])

@app.route('/api/prompts/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    # Правка 1: Честный 404 вместо падения
    conn = get_db_connection()
    p = conn.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,)).fetchone()
    conn.close()
    if not p:
        return jsonify({"error": "Prompt not found"}), 404
    return jsonify(dict(p))

@app.route('/api/prompts/<int:prompt_id>/components', methods=['POST'])
def add_component_to_prompt(prompt_id):
    # Правка 2: Проверка существования перед вставкой (защита от 500 IntegrityError)
    conn = get_db_connection()
    if not conn.execute('SELECT 1 FROM prompts WHERE id = ?', (prompt_id,)).fetchone():
        conn.close()
        return jsonify({"error": "Prompt not found"}), 404
    
    data = request.json
    cursor = conn.cursor()
    cursor.execute('INSERT INTO components (prompt_id, type, content) VALUES (?, ?, ?)',
                   (prompt_id, data.get('type'), data.get('content')))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"}), 201

@app.route('/api/validate', methods=['POST'])
def validate_prompt():
    data = request.json
    text = data.get('text', '').lower()
    
    # Правка 3: Умный валидатор (живые правила)
    checks = {
        "Role (Роль)": bool(re.search(r'\b(роль|role|act as|ты\s*[-—–]\s*|ты являешься|действуй как)\b', text)),
        "Task (Задача)": bool(re.search(r'\b(задача|task|сделай|выполни|напиши)\b', text)),
        "Context (Контекст)": bool(re.search(r'\b(контекст|context|фон|условия)\b', text)),
        "Format (Формат)": bool(re.search(r'\b(формат|format|выведи|верни в виде)\b', text)),
    }
    
    contradictions = []
    if re.search(r'\b(кратко|коротко|сжато|brief|short|в двух словах)\b', text) and \
       re.search(r'\b(подробно|детально|развернуто|detailed|extensive|максимально полно)\b', text):
        contradictions.append("⚠️ Противоречие: 'краткость' и 'подробность' одновременно.")

    ban_code = re.search(r'\b(без кода|no code|без примеров кода|только текст)\b', text)
    asks_code = re.search(r'\b(напиши|написать|верни|используй|добавь|включи|нужен|покажи)\b[^.!?]{0,40}\b(код|скрипт|функци)', text)
    if ban_code and asks_code:
        contradictions.append("⚠️ Противоречие: запрет на код и просьба дать код.")

    return jsonify({"checks": checks, "contradictions": contradictions})


@app.route('/')
def forge_index():
    return render_template('forge.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=is_debug)
