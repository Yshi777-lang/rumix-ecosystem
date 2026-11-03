# terminal_ws.py — безопасный терминал (v2, по образцу Horus)
# Создано: 30.10.2026 (Тиамат + Зая)

import os
import pty
import select
import time
import signal
import struct
import fcntl
import termios
from flask import session
from flask_socketio import SocketIO, emit

# Лимиты (как в Horus)
MAX_OUTPUT_BYTES = 16 * 1024
OUTPUT_WINDOW_MS = 32
MAX_SESSIONS = 4

# Хранилище сессий: sid -> {"fd": int, "pid": int, "last_send": float, "buffer": bytearray}
SESSIONS = {}


def _check_auth():
    """Проверка сессии (PIN) или локального запроса (127.0.0.1)."""
    from flask import request
    if request.remote_addr in ('127.0.0.1', '::1'):
        return True
    return session.get('logged_in', False)


def _close_session(sid):
    """Закрыть PTY и убить процесс."""
    if sid in SESSIONS:
        s = SESSIONS[sid]
        try:
            os.close(s['fd'])
        except OSError:
            pass
        try:
            os.kill(s['pid'], signal.SIGHUP)
        except OSError:
            pass
        del SESSIONS[sid]


def _read_loop(socketio, sid):
    """Читает PTY и отправляет кадры (с троттлингом)."""
    while sid in SESSIONS:
        s = SESSIONS[sid]
        r, _, _ = select.select([s['fd']], [], [], 0.1)
        if r:
            try:
                data = os.read(s['fd'], 4096)
                if not data:
                    break
                s['buffer'].extend(data)
                # Троттлинг: отправляем не чаще, чем раз в 32 мс
                now = time.time()
                if (now - s['last_send']) * 1000 >= OUTPUT_WINDOW_MS:
                    chunk = bytes(s['buffer'][:MAX_OUTPUT_BYTES])
                    s['buffer'] = s['buffer'][MAX_OUTPUT_BYTES:]
                    socketio.emit('terminal_output', {'data': chunk.decode(errors='replace')}, to=sid)
                    s['last_send'] = now
            except OSError:
                break
        else:
            # Если буфер есть, но таймаут — отправляем остаток
            if s['buffer']:
                now = time.time()
                if (now - s['last_send']) * 1000 >= OUTPUT_WINDOW_MS:
                    chunk = bytes(s['buffer'])
                    s['buffer'].clear()
                    socketio.emit('terminal_output', {'data': chunk.decode(errors='replace')}, to=sid)
                    s['last_send'] = now
    _close_session(sid)


def register_terminal_ws(socketio):
    @socketio.on('connect')
    def on_connect():
        if not _check_auth():
            print('[terminal_ws] connect: не авторизован, отключаю', flush=True)
            emit('terminal_error', {'error': 'Введите PIN в Shell, чтобы открыть терминал'})
            return False  # отключаем

    @socketio.on('terminal_start')
    def on_start(data=None):
        from flask import request
        sid = request.sid
        if sid in SESSIONS:
            return
        if len(SESSIONS) >= MAX_SESSIONS:
            emit('terminal_error', {'error': 'Слишком много сессий'})
            return
        pid, fd = pty.fork()
        if pid == 0:
            os.execvp('bash', ['bash'])
        else:
            SESSIONS[sid] = {'fd': fd, 'pid': pid, 'last_send': 0.0, 'buffer': bytearray()}
            socketio.start_background_task(_read_loop, socketio, sid)

    @socketio.on('terminal_input')
    def on_input(data):
        from flask import request
        sid = request.sid
        if sid not in SESSIONS:
            emit('terminal_error', {'error': 'Сессия не найдена'})
            return
        try:
            os.write(SESSIONS[sid]['fd'], data.get('data', '').encode())
        except OSError:
            _close_session(sid)

    @socketio.on('terminal_resize')
    def on_resize(data):
        from flask import request
        sid = request.sid
        if sid not in SESSIONS:
            return
        try:
            winsize = struct.pack('HHHH', data.get('rows', 24), data.get('cols', 80), 0, 0)
            fcntl.ioctl(SESSIONS[sid]['fd'], termios.TIOCSWINSZ, winsize)
        except OSError:
            pass

    @socketio.on('disconnect')
    def on_disconnect():
        from flask import request
        _close_session(request.sid)
