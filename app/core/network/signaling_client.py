# app/core/network/signaling_client.py
import socketio
import threading
import json
import uuid
from typing import Callable, Any

# --- ЗАМЕНИТЕ НА ВАШ URL С RENDER ---
# Убедитесь, что URL содержит только допустимые символы без пробелов
SERVER_URL = "https://fool-p2p-app.onrender.com"
# --- КОНЕЦ ЗАМЕНЫ ---

class SignalingClient:
    def __init__(self, on_signal: Callable[[dict], None]):
        """
        :param on_signal: Callback функция, вызываемая при получении сигнала от другого клиента.
        """
        # Указываем transports явно, иногда это помогает
        self.sio = socketio.Client()
        self.room = None
        self.client_id = str(uuid.uuid4())  # Генерируем уникальный ID
        self.on_signal_callback = on_signal
        self.found_host_callback = None
        self.is_host = False
        self.room_password = None
        self._setup_events()
        print(f"SignalingClient initialized. Client ID: {self.client_id}")
        print(f"Target server URL: '{SERVER_URL}'")

    def _setup_events(self):
        @self.sio.event
        def connect():
            print(f"[SocketIO Event] Connected to signaling server: {SERVER_URL}")
            print(f"[SocketIO Event] Assigned SID: {self.sio.sid if hasattr(self.sio, 'sid') else 'N/A'}")
            # Автоматически присоединяемся к комнате после подключения
            if self.room:
                self._join_room_internal()

        @self.sio.event
        def disconnect():
            print("[SocketIO Event] Disconnected from signaling server")

        @self.sio.event
        def connect_error(data):
             # Обрабатываем ошибку подключения на уровне SocketIO
             print(f"[SocketIO Event] Connection Error: {data}")
             # data может содержать словарь с 'message' и 'error'
             if isinstance(data, dict):
                 message = data.get('message', 'Unknown connection error (dict)')
                 error_details = data.get('error', '')
                 print(f"  - Message: {message}")
                 if error_details:
                     print(f"  - Error Details: {error_details}")
             else:
                 print(f"  - Error Data (raw): {data}")


        @self.sio.on('joined')
        def on_joined(data):
            status = data.get('status')
            message = data.get('message', '')
            print(f"[SocketIO Event] 'joined' received: status={status}, message={message}")
            
            if status == 'success':
                print(f"Successfully joined room: {self.room}")
                # Если мы хост, сообщаем об этом
                if self.is_host:
                    self._announce_host()
            elif status == 'error':
                print(f"Failed to join room: {message}")

        @self.sio.on('signal')
        def on_signal(data):
            print(f"[SocketIO Event] 'signal' received: type={data.get('type', 'unknown')}")
            if self.on_signal_callback:
                self.on_signal_callback(data)

        @self.sio.on('host_available')
        def on_host_available(data):
            host_id = data.get('host_id')
            room = data.get('room')
            print(f"[SocketIO Event] 'host_available' received: host_id={host_id}, room={room}")
            if not self.is_host and host_id != self.client_id:
                # Если мы не хост и это не наш ID, пытаемся подключиться
                if self.found_host_callback:
                    self.found_host_callback(host_id)
                else:
                    print("Host found, but no callback set")

    def connect(self):
        """Подключается к серверу в отдельном потоке, чтобы не блокировать UI."""
        def run():
            try:
                print(f"[Connect Method] Attempting to connect to {SERVER_URL}")
                # Добавим больше информации о попытке подключения
                print(f"[Connect Method] Using transports: ['websocket', 'polling']")
                # Попробуем с reconnection=False, чтобы сразу увидеть ошибку
                self.sio.connect(SERVER_URL, transports=['websocket', 'polling'], wait_timeout=10) # Увеличиваем wait_timeout
                print("[Connect Method] SocketIO connection established, starting wait loop...")
                self.sio.wait()  # Блокирует поток, ожидая события
                print("[Connect Method] SocketIO wait loop ended.")
            except socketio.exceptions.ConnectionError as conn_err:
                # Более конкретная обработка ошибки подключения
                print(f"[Connect Method] SignalingClient connection error (ConnectionError): {conn_err}")
                # Попробуем получить больше деталей, если возможно
                print(f"  - Type: {type(conn_err)}")
                if hasattr(conn_err, '__cause__') and conn_err.__cause__:
                     print(f"  - Cause: {conn_err.__cause__}")
                     print(f"  - Cause Type: {type(conn_err.__cause__)}")
                # Выводим traceback для полной информации
                import traceback
                print("[Connect Method] Full traceback for ConnectionError:")
                traceback.print_exc()
            except Exception as e:
                # Остальные ошибки
                print(f"[Connect Method] SignalingClient connection error (General Exception): {e}")
                print(f"  - Type: {type(e)}")
                import traceback
                print("[Connect Method] Full traceback for General Exception:")
                traceback.print_exc()

        print("[Connect Method] Starting connection thread...")
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        print("[Connect Method] Connection thread started.")

    def join_room(self, room_name: str, password: str = None):
        """Публичный метод для присоединения к комнате."""
        print(f"[Join Room Method] Request to join room: {room_name}")
        self.room = room_name
        self.room_password = password
        if self.sio.connected:
            print("[Join Room Method] Already connected, joining room immediately.")
            self._join_room_internal()
        else:
             print("[Join Room Method] Not connected yet, room will be joined after connection.")
        # Если не подключены, комната будет присоединена при подключении

    def _join_room_internal(self):
        """Внутренний метод присоединения к комнате."""
        try:
            payload = {
                'room': self.room,
                'password': self.room_password,
                'is_host': self.is_host
            }
            print(f"[_join_room_internal] Emitting 'join' with payload: {payload}")
            self.sio.emit('join', payload)
            print(f"[_join_room_internal] 'join' event emitted for room: {self.room}")
        except Exception as e:
            print(f"[_join_room_internal] Error emitting 'join' event: {e}")
            print(f"  - Type: {type(e)}")
            import traceback
            print("[_join_room_internal] Full traceback:")
            traceback.print_exc()

    def _announce_host(self):
        """Объявляем себя как хост."""
        if self.room and self.client_id:
            payload = {
                'host_id': self.client_id,
                'room': self.room
            }
            try:
                print(f"[_announce_host] Emitting 'host_available' with payload: {payload}")
                self.sio.emit('host_available', payload)
                print(f"[_announce_host] 'host_available' event emitted for room {self.room}")
            except Exception as e:
                print(f"[_announce_host] Error emitting 'host_available' event: {e}")
                print(f"  - Type: {type(e)}")
                import traceback
                print("[_announce_host] Full traceback:")
                traceback.print_exc()

    def send_signal(self, target_id: str, signal_data: dict):
        """
        Отправляет сигнал (offer, answer, ice_candidate) другому клиенту через сервер.
        :param target_id: ID клиента-получателя.
        :param signal_data: Словарь с данными сигнала (sdp или candidate).
        """
        if not self.room:
            print("[send_signal] Error: Not in a room")
            return
            
        payload = {
            'sender': self.client_id,
            'target': target_id,
            'room': self.room,
            'type': signal_data.get('type'),
            'data': signal_data
        }
        print(f"[send_signal] Emitting 'signal' to {target_id} via server: type={signal_data.get('type')}")
        try:
            self.sio.emit('signal', payload)
            print(f"[send_signal] 'signal' event emitted successfully.")
        except Exception as e:
            print(f"[send_signal] Error emitting 'signal' event: {e}")
            print(f"  - Type: {type(e)}")
            import traceback
            print("[send_signal] Full traceback:")
            traceback.print_exc()

    def found_host(self, host_id: str):
        """Вызывается, когда найден доступный хост"""
        print(f"[found_host] Callback called with host_id: {host_id}")
        if self.found_host_callback:
            self.found_host_callback(host_id)
        else:
             print("[found_host] No callback function set.")

# --- Пример использования (для тестирования отдельно) ---
if __name__ == "__main__":
    def my_signal_handler(data):
        print("App received signal:", data.get('type', 'unknown'))

    def my_host_handler(host_id):
        print("App found host:", host_id)

    client = SignalingClient(on_signal=my_signal_handler)
    client.found_host_callback = my_host_handler
    client.connect()
    # client.join_room("test_room") # Попробуйте вызвать join_room позже, после подключения

    # Чтобы скрипт не завершался
    try:
        while True:
            pass
    except KeyboardInterrupt:
        if client.sio.connected:
            client.sio.disconnect()