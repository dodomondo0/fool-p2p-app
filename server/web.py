from signaling_server import app, socketio
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting web server on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, log_output=True)