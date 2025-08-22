# server/gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:10000"
# Используем 1 воркер, так как Socket.IO требует обмен сообщениями между воркерами,
# что сложно настроить без брокера сообщений (Redis).
workers = 1
# worker_class = "sync" # УДАЛИТЬ
# Для Flask-SocketIO с eventlet
worker_class = "eventlet"
# Если eventlet не работает, попробуйте gevent (нужно установить gevent и gevent-websocket):
# worker_class = "geventwebsocket.gunicorn.workers.GeventWebSocketWorker"

worker_connections = 1000
# Увеличиваем таймаут
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True