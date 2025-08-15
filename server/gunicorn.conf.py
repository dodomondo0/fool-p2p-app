# Gunicorn configuration for Render
bind = "0.0.0.0:10000"
workers = 1
# Используем стандартный worker вместо eventlet из-за проблем с Python 3.13
worker_class = "sync"
# worker_class = "eventlet"  # Закомментируем это
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True