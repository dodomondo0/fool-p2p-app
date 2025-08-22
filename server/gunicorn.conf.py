# server/gunicorn.conf.py
# Конфигурация для Gunicorn
# Render может использовать эту конфигурацию или переопределять её.
# Убедитесь, что она совместима.

bind = "0.0.0.0:10000"
workers = 1 # Для Socket.IO часто используется 1 worker
worker_class = "sync" # Используем sync worker, совместимый с threading
worker_connections = 1000
timeout = 120 # Увеличиваем таймаут
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
