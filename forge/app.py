import os, re, sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "rumix-secret")
ALLOWED_ORIGINS = {'http://127.0.0.1:8001', 'http://127.0.0.1:5001', 'http://localhost:8001'}

@app.before_request
def check_origin():
    if request.method in ['POST', 'PUT', 'DELETE']:
        origin = request.headers.get('Origin')
        if origin and origin not in ALLOWED_ORIGINS:
            return jsonify({"error": "Unauthorized origin"}), 403

def get_db():
    conn = sqlite3.connect('forge.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS prompts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, raw_content TEXT, status TEXT DEFAULT 'draft', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS components (id INTEGER PRIMARY KEY AUTOINCREMENT, prompt_id INTEGER, type TEXT, content TEXT, FOREIGN KEY (prompt_id) REFERENCES prompts (id))''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index(): return render_template('forge.html')

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    conn = get_db()
    prompts = conn.execute('SELECT id, title, raw_content, status, created_at FROM prompts ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(p) for p in prompts])

@app.route('/api/prompts', methods=['POST'])
def save_prompt():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO prompts (title, raw_content) VALUES (?, ?)', (data.get('title'), data.get('raw_content')))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"}), 201

@app.route('/api/validate', methods=['POST'])
def validate():
    text = request.json.get('text', '').lower()
    checks = {"Role": bool(re.search(r'\b(роль|role|ты\s*[-—–]\s*|действуй как)\b', text)), "Task": bool(re.search(r'\b(задача|сделай|напиши)\b', text))}
    return jsonify({"checks": checks, "contradictions": []})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
