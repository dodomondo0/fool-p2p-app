# server/web.py
# Этот файл служит точкой входа для WSGI-сервера (например, Render).
# Он импортирует приложение Flask и SocketIO, но НЕ запускает сервер.

from signaling_server import app, socketio

# Render будет использовать переменную 'app' как WSGI-приложение.
# SocketIO уже прикреплен к app внутри signaling_server.py