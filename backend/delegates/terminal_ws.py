# terminal_ws.py — настоящий терминал через PTY и WebSocket
# Создано: 19.10.2026 (Тиамат + Зая)

import os
import pty
import select
from flask_socketio import SocketIO, emit

def register_terminal_ws(socketio):
    @socketio.on('terminal_input')
    def handle_terminal_input(data):
        # Запускаем PTY (один раз)
        if not hasattr(socketio, 'pty_fd'):
            pid, fd = pty.fork()
            if pid == 0:
                # Дочерний процесс — запускаем bash
                os.execvp('bash', ['bash'])
            else:
                socketio.pty_fd = fd
                socketio.pty_pid = pid

        # Отправляем ввод в PTY
        os.write(socketio.pty_fd, data['data'].encode())

    @socketio.on('terminal_resize')
    def handle_terminal_resize(data):
        # Изменяем размер терминала
        if hasattr(socketio, 'pty_fd'):
            import fcntl, termios, struct
            winsize = struct.pack('HHHH', data['rows'], data['cols'], 0, 0)
            fcntl.ioctl(socketio.pty_fd, termios.TIOCSWINSZ, winsize)

    # Фоновый поток для чтения из PTY
    def read_pty():
        while True:
            if hasattr(socketio, 'pty_fd'):
                r, _, _ = select.select([socketio.pty_fd], [], [], 0.1)
                if r:
                    try:
                        data = os.read(socketio.pty_fd, 1024)
                        socketio.emit('terminal_output', {'data': data.decode(errors='replace')})
                    except OSError:
                        break
    socketio.start_background_task(read_pty)
