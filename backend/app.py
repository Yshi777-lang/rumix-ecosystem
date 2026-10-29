from flask import Flask, send_from_directory, jsonify, request, session
import subprocess
import json
import os

app = Flask(__name__)
app.secret_key = "rumix_secret_key_2026"
from flask_socketio import SocketIO
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:8001", "http://localhost:8001"], async_mode="threading")

# Ядро файлового менеджера (порт из Twig)
import sys as _sys
_sys.path.insert(0, '/data/data/com.termux/files/home/rumix')
try:
    from core.fs.registry import FsRegistry
    from core.fs.fs_local import LocalFileSystem
    if not FsRegistry.all():
        FsRegistry.register(LocalFileSystem(root_dir=os.path.expanduser('~'), display_name='Local'))
except Exception as _e:
    print("FS core init failed:", _e)


@app.route('/maigret')
def maigret_page():
    return send_from_directory('../web', 'maigret.html')

@app.route('/terminal')
def terminal_page():
    return send_from_directory('../web', 'terminal.html')

@app.route('/')
def index():
    return send_from_directory('../web', 'index.html')


@app.before_request
def check_auth():
    # Разрешаем без авторизации только вход и статус
    if request.path.startswith('/static/') or request.path in ['/api/pin/check', '/api/pin/status', '/api/status', '/api/agent/status', '/', '/terminal']:
        return
    # Если PIN не установлен — пускаем всех (первый запуск)
    if not os.path.exists(PIN_FILE):
        return
    # Всё остальное — только с сессией
    return  # проверка отключена (временно)

@app.route('/api/agent/status')
def agent_status():
    import json
    from pathlib import Path
    f = Path.home() / '.rumix_status.json'
    if f.exists():
        try:
            return jsonify(json.loads(f.read_text(encoding='utf-8')))
        except Exception:
            pass
    return jsonify({'status': 'idle'})

@app.route('/api/status')
def status():
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../scripts/check-rumix.sh')
    try:
        result = subprocess.run(
            [script_path, '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return jsonify({'ok': False, 'regression': 'ERROR', 'drift': 'Скрипт упал', 'agents': 0, 'loop': 'UNKNOWN'}), 500
        data = json.loads(result.stdout.strip())
        return jsonify(data)
    except json.JSONDecodeError:
        return jsonify({'ok': False, 'regression': 'PARSE_ERROR', 'drift': 'Неверный формат', 'agents': 0, 'loop': 'UNKNOWN'}), 500
    except FileNotFoundError:
        return jsonify({'ok': False, 'regression': 'FILE_NOT_FOUND', 'drift': 'Скрипт не найден', 'agents': 0, 'loop': 'UNKNOWN'}), 404
    except Exception as e:
        return jsonify({'ok': False, 'regression': 'UNKNOWN_ERROR', 'drift': str(e), 'agents': 0, 'loop': 'UNKNOWN'}), 500

@app.route('/api/logs')
def logs():
    import os
    log_path = os.path.expanduser('~/rumix/logs/shell.log')
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        limit = int(request.args.get('limit', 50))
        return jsonify({'lines': [l.rstrip() for l in lines[-limit:]]})
    except FileNotFoundError:
        return jsonify({'lines': ['Лог пуст']})
    except Exception as e:
        return jsonify({'lines': [f'[ERROR] {e}']})

@app.route('/api/files')
def files():
    try:
        from core.fs.registry import FsRegistry
        from core.fs.fs_exception import FsException
        from core.fs.fs_zip import ZipFileSystem
        from core.fs.fs_tar import TarFileSystem
        path = request.args.get('path') or os.path.expanduser('~')
        scheme = request.args.get('scheme') or 'file'
        host = request.args.get('host')
        # Проверка file_gate
        from core.bridge.file_gate import check_file
        gate = check_file(path, 'read')
        if not gate['allowed']:
            return jsonify({'error': gate['message']}), 403

        if scheme == 'zip':
            if not host: return jsonify({'error': 'host required for zip'}), 400
            fs = ZipFileSystem(host)
        elif scheme == 'tar':
            if not host: return jsonify({'error': 'host required for tar'}), 400
            fs = TarFileSystem(host)
        else:
            fs = FsRegistry.of(scheme)

        entry = fs.stat(path)
        if entry is None:
            return jsonify({'error': 'Not found: ' + path}), 404
        if not entry.is_dir:
            return jsonify({'error': 'Not a directory: ' + path}), 400
        items = []
        for f in fs.list(entry):
            items.append({
                'name': f.name, 'path': f.path,
                'type': 'dir' if f.is_dir else 'file',
                'size': f.size, 'mtime': f.last_modified,
                'can_read': f.can_read, 'can_write': f.can_write,
                'scheme': f.scheme,
            })
        return jsonify({'path': entry.path, 'scheme': scheme, 'host': host, 'items': items})
    except FsException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/translate', methods=['POST'])
def api_translate():
    try:
        from core.translate import translate
        data = request.get_json() or {}
        text = data.get('text', '')
        src = data.get('src', 'en')
        trg = data.get('trg', 'ru')
        if not text: return jsonify({'error': 'text required'}), 400
        out = translate(text, src, trg)
        return jsonify({'ok': True, 'result': out, 'src': src, 'trg': trg})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adb/connect', methods=['POST'])
def adb_connect():
    try:
        from core.adb_manager import AdbManager
        data = request.get_json() or {}
        host = data.get('host', '127.0.0.1')
        port = int(data.get('port', 5555))
        res = AdbManager().connect(host, port)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adb/apps', methods=['GET'])
def adb_apps():
    try:
        from core.adb_manager import AdbManager
        apps = AdbManager().list_apps()
        return jsonify({'apps': apps})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adb/shell', methods=['POST'])
def adb_shell():
    try:
        from core.adb_manager import AdbManager
        data = request.get_json() or {}
        cmd = data.get('cmd')
        if not cmd: return jsonify({'error': 'cmd required'}), 400
        res = AdbManager().shell(cmd)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adb/install', methods=['POST'])
def adb_install():
    try:
        from core.adb_manager import AdbManager
        data = request.get_json() or {}
        path = data.get('path')
        if not path: return jsonify({'error': 'path required'}), 400
        res = AdbManager().install_apk(path)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/adb/action', methods=['POST'])
def adb_action():
    try:
        from core.adb_manager import AdbManager
        data = request.get_json() or {}
        pkg, action = data.get('pkg'), data.get('action')
        if not pkg or not action: return jsonify({'error': 'pkg and action required'}), 400
        res = AdbManager().action_app(pkg, action)
        return jsonify(res)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def api_search():
    try:
        from core.maigret import search_username
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        if not username:
            return jsonify({'error': 'username required'}), 400
        no_recursion = data.get('no_recursion', True)
        no_extracting = data.get('no_extracting', True)
        top_sites = int(data.get('top_sites', 0))
        result = search_username(username, no_recursion=no_recursion, no_extracting=no_extracting, top_sites=top_sites)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mode', methods=['GET', 'POST'])
def api_mode():
    try:
        from core.bridge.permission_mode import PermissionMode
        if request.method == 'GET':
            return jsonify(PermissionMode.status())
        data = request.get_json() or {}
        name = data.get('mode')
        if not name:
            return jsonify({'error': 'mode required'}), 400
        result = PermissionMode.set_by_name(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/speak', methods=['POST'])
def api_speak():
    try:
        from core.voice import speak
        data = request.get_json() or {}
        text = data.get('text', '')
        if not text: return jsonify({'error': 'text required'}), 400
        ok = speak(text)
        return jsonify({'ok': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/extract', methods=['POST'])
def files_extract():
    """Распаковать архив. body: {"host": "...", "scheme": "zip|tar", "dest": "..."}"""
    try:
        import zipfile, tarfile, time
        from pathlib import Path as _P
        data = request.get_json() or {}
        host = data.get('host')
        scheme = data.get('scheme') or 'zip'
        dest = data.get('dest')
        if not host:
            return jsonify({'error': 'host required'}), 400
        hp = _P(host)
        if not hp.exists():
            return jsonify({'error': 'Archive not found: ' + host}), 404
        if not dest:
            dest = str(hp.parent)
        dp = _P(dest)
        dp.mkdir(parents=True, exist_ok=True)

        count = 0
        if scheme == 'zip':
            with zipfile.ZipFile(str(hp), 'r') as z:
                z.extractall(str(dp), members=[m for m in z.namelist() if not m.startswith("/") and ".." not in m])
                count = len(z.namelist())
        elif scheme == 'tar':
            with tarfile.open(str(hp), 'r:*') as t:
                t.extractall(str(dp), members=[m for m in t.getmembers() if not m.name.startswith("/") and ".." not in m.name])
                count = len(t.getnames())
        else:
            return jsonify({'error': 'Unsupported scheme: ' + scheme}), 400

        return jsonify({'ok': True, 'dest': str(dp), 'files': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/archive', methods=['POST'])
def files_archive():
    """Создать ZIP из папки. body: {"path": "/abs/path"}"""
    try:
        import zipfile, time
        from core.fs.registry import FsRegistry
        from core.fs.fs_exception import FsException
        from pathlib import Path as _P
        data = request.get_json() or {}
        src = data.get('path')
        if not src:
            return jsonify({'error': 'path required'}), 400
        fs = FsRegistry.of('file')
        entry = fs.stat(src)
        if entry is None:
            return jsonify({'error': 'Not found: ' + src}), 404
        if not entry.is_dir:
            return jsonify({'error': 'Not a directory: ' + src}), 400
        ts = time.strftime('%Y%m%d_%H%M%S')
        out_path = str(_P(src) / ('archive_' + ts + '.zip'))
        base = _P(src)
        count = 0
        with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in fs.list(entry):
                ip = _P(item.path)
                if ip.name.startswith('archive_') and ip.suffix == '.zip':
                    continue
                if item.is_dir:
                    for f in ip.rglob('*'):
                        if f.is_file():
                            z.write(str(f), str(f.relative_to(base)))
                            count += 1
                else:
                    z.write(str(ip), str(ip.relative_to(base)))
                    count += 1
        size = _P(out_path).stat().st_size
        return jsonify({'ok': True, 'output': out_path, 'files': count, 'size': size})
    except FsException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/read')
def files_read():
    """Прочитать файл через ядро ФС. ?path=...&scheme=file"""
    try:
        from core.fs.registry import FsRegistry
        from core.fs.fs_exception import FsException
        path = request.args.get('path')
        if not path:
            return jsonify({'error': 'path required'}), 400
        gate = check_file(path, 'read')
        if not gate['allowed']:
            return jsonify({'error': gate['message']}), 403
        scheme = request.args.get('scheme') or 'file'
        host = request.args.get('host')
        from core.fs.fs_zip import ZipFileSystem
        from core.fs.fs_tar import TarFileSystem
        if scheme == 'zip':
            if not host: return jsonify({'error': 'host required for zip'}), 400
            fs = ZipFileSystem(host)
        elif scheme == 'tar':
            if not host: return jsonify({'error': 'host required for tar'}), 400
            fs = TarFileSystem(host)
        else:
            fs = FsRegistry.of(scheme)
        entry = fs.stat(path)
        if entry is None:
            return jsonify({'error': 'Not found: ' + path}), 404
        if entry.is_dir:
            return jsonify({'error': 'Is a directory: ' + path}), 400
        if entry.size > 1024 * 1024:
            return jsonify({'error': 'File too large (>1MB)', 'size': entry.size}), 413
        with fs.open_input(entry) as f:
            data = f.read()
        try:
            text = data.decode('utf-8')
            return jsonify({'path': entry.path, 'size': entry.size, 'type': 'text', 'content': text})
        except UnicodeDecodeError:
            import base64
            return jsonify({'path': entry.path, 'size': entry.size, 'type': 'binary', 'content': base64.b64encode(data).decode()})
    except FsException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/action', methods=['POST'])
def action():
    import subprocess, os
    data = request.json or {}
    action_name = data.get('action', '')
    scripts_dir = os.path.expanduser('~/rumix/scripts')
    allowed = {
        'audit':   ['bash', os.path.join(scripts_dir, 'check-rumix.sh')],
        'backup':  ['bash', os.path.join(scripts_dir, 'backup.sh')],
        'audit-all': ['bash', os.path.join(scripts_dir, 'audit-all.sh')],
        'stop':    ['bash', os.path.join(scripts_dir, 'shell-stop.sh')],
        'fury':         ['bash', os.path.join(scripts_dir, 'fury.sh')],
        'runtime':      ['bash', os.path.join(scripts_dir, 'agents-menu.sh')],
        'install_neon': ['bash', os.path.join(scripts_dir, 'install-neon.sh')],
        'projects':     ['bash', os.path.join(scripts_dir, 'projects-menu.sh')],
        'upgrade':      ['bash', '-c', 'pkg update -y && pkg upgrade -y'],
    }
    if action_name not in allowed:
        return jsonify({'ok': False, 'error': f'Действие "{action_name}" не разрешено'}), 400
    try:
        result = subprocess.run(
            allowed[action_name],
            capture_output=True, text=True, timeout=300
        )
        return jsonify({
            'ok': result.returncode == 0,
            'action': action_name,
            'stdout': result.stdout[-2000:],
            'stderr': result.stderr[-500:],
            'exit': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'ok': False, 'error': 'Таймаут (300s)'}), 504
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

# --- PIN-защита ---
PIN_FILE = os.path.expanduser('~/.rumix-pin')

@app.route('/api/pin/check', methods=['POST'])
def pin_check():
    import hashlib
    data = request.json or {}
    pin = data.get('pin', '')
    if not pin:
        return jsonify({'ok': False, 'error': 'Пустой PIN'}), 400
    try:
        with open(PIN_FILE, 'r') as f:
            stored = f.read().strip()
    except FileNotFoundError:
        session['logged_in'] = True
        return jsonify({'ok': True, 'note': 'PIN не установлен'})
    provided = hashlib.sha256(pin.encode()).hexdigest()
    if provided == stored:
        session['logged_in'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'Неверный PIN'}), 401

@app.route('/api/pin/set', methods=['POST'])
def pin_set():
    import hashlib
    data = request.json or {}
    pin = data.get('pin', '')
    if not pin or len(pin) < 4:
        return jsonify({'ok': False, 'error': 'PIN минимум 4 символа'}), 400
    try:
        with open(PIN_FILE, 'w') as f:
            f.write(hashlib.sha256(pin.encode()).hexdigest())
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/pin/status')
def pin_status():
    import os as _os
    return jsonify({'set': _os.path.exists(PIN_FILE)})

# --- Меню Rumix ---
@app.route('/api/instruction')
def instruction():
    import os
    path = os.path.expanduser('~/Work/blocks/cards/rumix-first-time.md')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return jsonify({'content': f.read()})
    except FileNotFoundError:
        return jsonify({'content': 'Инструкция не найдена'}), 404
    except Exception as e:
        return jsonify({'content': f'[ERROR] {e}'}), 500

@app.route('/api/projects')
def projects():
    import os
    home = os.path.expanduser('~')
    projects = [
        {'icon': '🌿', 'name': 'Work (душа дома)', 'path': f'{home}/Work', 'desc': 'Ядро, летопись, карты'},
        {'icon': '🧬', 'name': 'Rumix (тело дома)', 'path': f'{home}/rumix', 'desc': 'Терминал, скрипты, Agent Runtime'},
        {'icon': '🧪', 'name': 'Tiamat-ai- (лаборатория)', 'path': f'{home}/Tiamat-ai-', 'desc': 'Эксперименты, NobodyWho, APK'},
        {'icon': '🤖', 'name': 'Deepseek-API', 'path': f'{home}/Deepseek-API', 'desc': 'API эксперимент (отложен)'},
        {'icon': '📦', 'name': 'models', 'path': f'{home}/models', 'desc': 'Локальные LLM (Qwen 0.6B, 1.5B)'},
        {'icon': '💾', 'name': 'Download', 'path': f'{home}/storage/shared/Download', 'desc': 'Загрузки, бекапы'},
    ]
    return jsonify({'projects': projects})

@app.route('/static/dragon-rumix.png')
def dragon():
    import os
    from flask import send_file
    path = os.path.expanduser('~/Work/assets/dragon-rumix.png')
    if not os.path.exists(path):
        return 'Not found', 404
    return send_file(path, mimetype='image/png')

# --- Bridge API: Loop ---
import uuid as _uuid

BRIDGE_TASKS = {}

@app.route('/api/bridge/health')
def bridge_health():
    import os
    loop_dir = os.path.expanduser('~/rumix/loop')
    state_file = os.path.join(loop_dir, 'state.json')
    state = 'unknown'
    try:
        with open(state_file) as f:
            import json as _json
            state = _json.load(f).get('state', 'unknown')
    except Exception:
        pass
    return jsonify({'ok': True, 'loop': state, 'loop_dir': loop_dir})

@app.route('/api/bridge/tasks', methods=['POST'])
def bridge_task_create():
    import subprocess, os
    data = request.json or {}
    name = data.get('name', '').strip()
    script = data.get('script', '').strip()

    if not name or not script:
        return jsonify({'ok': False, 'error': 'name и script обязательны'}), 400

    # Валидация имени
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return jsonify({'ok': False, 'error': 'name: только [a-zA-Z0-9_-]'}), 400

    # Whitelist: только известные команды
    allowed_prefixes = [
        'echo ', 'ls ', 'pwd', 'whoami', 'date', 'uname',
        'check-rumix', 'check-config-drift', 'pgrep ', 'curl -s http://127.0.0.1:8001',
    ]
    if not any(script.startswith(p) for p in allowed_prefixes):
        return jsonify({'ok': False, 'error': 'Команда не в whitelist'}), 403

    # Генерируем ID
    task_id = f'bridge-{_uuid.uuid4().hex[:8]}'

    loop_submit = os.path.expanduser('~/rumix/loop/loop-submit.sh')
    try:
        r = subprocess.run(
            [loop_submit, task_id],
            input=script,
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0:
            return jsonify({'ok': False, 'error': 'Loop отклонил', 'stderr': r.stderr}), 500
        return jsonify({'ok': True, 'id': task_id, 'stdout': r.stdout}), 201
    except subprocess.TimeoutExpired:
        return jsonify({'ok': False, 'error': 'Timeout'}), 504
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/bridge/tasks/<task_id>')
def bridge_task_get(task_id):
    import os, re
    if not re.match(r'^[a-zA-Z0-9_-]+$', task_id):
        return jsonify({'ok': False, 'error': 'bad id'}), 400
    in_file = os.path.expanduser(f'~/rumix/loop/in/{task_id}.result')
    if not os.path.exists(in_file):
        return jsonify({'ok': False, 'status': 'pending'})
    try:
        with open(in_file, 'r', encoding='utf-8') as f:
            return jsonify({'ok': True, 'status': 'done', 'result': f.read()})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# === Веб-терминал (Победа 87) ===
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/rumix')
from web.terminal_api import run_command

@app.route('/api/terminal', methods=['POST'])
def api_terminal():
    data = request.get_json()
    cmd = data.get('cmd', '')
    # consent больше не доверяем клиенту (безопасность)
    if not cmd:
        return jsonify({'status': 'ERROR', 'message': 'Пустая команда.'}), 400
    # Разрешаем только READ (без спроса), остальное — через AskUser внутри run_command
    result = run_command(cmd, user_consent=False)
    return jsonify(result)


# === Git Интеграция (Победа 88) ===
import os
from git_manager import get_status, rollback

@app.route('/api/git/status', methods=['GET'])
def api_git_status():
    return jsonify(get_status())

@app.route('/api/git/rollback', methods=['POST'])
def api_git_rollback():
    data = request.get_json()
    consent = data.get('consent', False)
    if not consent:
        return jsonify({'status': 'DENIED', 'message': 'Требуется разрешение Зая (consent: true).'}), 403
    return jsonify(rollback())



# === Самопроверка (Победа 89) ===
from backend.selftest import run_all

@app.route('/api/selftest', methods=['GET'])
def api_selftest():
    return jsonify(run_all())



# === Регистрация Blueprint (Победа 91) ===
from delegates.terminal_delegate import terminal_bp
app.register_blueprint(terminal_bp)

from delegates.git_delegate import git_bp
app.register_blueprint(git_bp)

from delegates.selftest_delegate import selftest_bp
app.register_blueprint(selftest_bp)

from delegates.menu_delegate import menu_bp
app.register_blueprint(menu_bp)

from delegates.chat_delegate import chat_bp
from delegates.terminal_ws import register_terminal_ws
app.register_blueprint(chat_bp)

# terminal_ws removed (security)
# register_terminal_ws(socketio) — временно отключено (pty)


# === Синхронизация (GitHub) ===
@app.route('/api/sync/control', methods=['POST'])
def sync_control():
    data = request.json or {}
    action = data.get('action', 'status')
    script = os.path.expanduser('~/rumix/scripts/sync-control.sh')
    
    try:
        result = subprocess.run(
            ['bash', script, action],
            capture_output=True, text=True, timeout=30
        )
        return jsonify({
            'ok': result.returncode == 0,
            'action': action,
            'output': result.stdout.strip(),
            'error': result.stderr.strip()
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500



# === HH Settings (автоотклики) ===
import json as _json
import os as _os

HH_ENV_PATH = _os.path.expanduser('~/Work/archive/hh-autoresponder-1.0.0/.env')

@app.route('/hh-settings')
def hh_settings_page():
    return send_from_directory('../web', 'hh-settings.html')

@app.route('/api/hh/settings', methods=['POST'])
def hh_settings_save():
    data = request.json or {}
    try:
        lines = []
        if _os.path.exists(HH_ENV_PATH):
            with open(HH_ENV_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        updated = []
        existing = set()
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                if key in data:
                    updated.append(f'{key}={data[key]}\n')
                    existing.add(key)
                else:
                    updated.append(line)
            else:
                updated.append(line)
        
        for key, value in data.items():
            if key not in existing:
                updated.append(f'{key}={value}\n')
        
        with open(HH_ENV_PATH, 'w', encoding='utf-8') as f:
            f.writelines(updated)
        
        return jsonify({'ok': True, 'message': 'Сохранено.'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8001, allow_unsafe_werkzeug=True)
