from signaling_server import app, socketio
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting web server on port {port}...")
    # Разрешаем использование Werkzeug в продакшене
    socketio.run(app, host='0.0.0.0', port=port, log_output=True, allow_unsafe_werkzeug=True)