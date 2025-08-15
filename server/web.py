# Этот файл больше не нужен при использовании Gunicorn
# Оставим его пустым или для совместимости
from signaling_server import app, socketio

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting web server on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, log_output=True, allow_unsafe_werkzeug=True)