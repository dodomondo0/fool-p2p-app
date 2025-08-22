import socketio
import threading
import json
import uuid
from typing import Callable, Any

# --- ЗАМЕНИТЕ НА ВАШ URL С RENDER ---
SERVER_URL = "https://fool-p2p-app.onrender.com"
# --- КОНЕЦ ЗАМЕНЫ ---

class SignalingClient:
    def __init__(self, on_signal: Callable[[dict], None]):
        """
        :param on_signal: Callback функция, вызываемая при получении сигнала от другого клиента.
        """
        self.sio = socketio.Client()
        self.room = None
        self.client_id = str(uuid.uuid4())  # Генерируем уникальный ID
        self.on_signal_callback = on_signal
        self.found_host_callback = None
        self.is_host = False
        self.room_password = None
        self._setup_events()
        print(f"Client ID created: {self.client_id}")

    def _setup_events(self):
        @self.sio.event
        def connect():
            print(f"Connected to signaling server: {SERVER_URL}")
            print(f"Client ID: {self.client_id}")
            # Автоматически присоединяемся к комнате после подключения
            if self.room:
                self._join_room_internal()

        @self.sio.event
        def disconnect():
            print("Disconnected from signaling server")

        @self.sio.on('joined')
        def on_joined(data):
            status = data.get('status')
            message = data.get('message', '')
            print(f"Join room response: {status} - {message}")
            
            if status == 'success':
                print(f"Successfully joined room: {self.room}")
                # Если мы хост, сообщаем об этом
                if self.is_host:
                    self._announce_host()
            elif status == 'error':
                print(f"Failed to join room: {message}")

        @self.sio.on('signal')
        def on_signal(data):
            print(f"Received signal via server: {data.get('type', 'unknown')}")
            if self.on_signal_callback:
                self.on_signal_callback(data)

        @self.sio.on('host_available')
        def on_host_available(data):
            host_id = data.get('host_id')
            room = data.get('room')
            print(f"Host available in room {room}: {host_id}")
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
                print(f"Connecting to {SERVER_URL}")
                self.sio.connect(SERVER_URL, transports=['websocket', 'polling'])
                self.sio.wait()  # Блокирует поток, ожидая события
            except Exception as e:
                print(f"SignalingClient connection error: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def join_room(self, room_name: str, password: str = None):
        """Публичный метод для присоединения к комнате."""
        self.room = room_name
        self.room_password = password
        if self.sio.connected:
            self._join_room_internal()
        # Если не подключены, комната будет присоединена при подключении

    def _join_room_internal(self):
        """Внутренний метод присоединения к комнате."""
        try:
            payload = {
                'room': self.room,
                'password': self.room_password,
                'is_host': self.is_host
            }
            self.sio.emit('join', payload)
            print(f"Join room request sent: {self.room}")
        except Exception as e:
            print(f"Error joining room: {e}")

    def _announce_host(self):
        """Объявляем себя как хост."""
        if self.room and self.client_id:
            payload = {
                'host_id': self.client_id,
                'room': self.room
            }
            try:
                self.sio.emit('host_available', payload)
                print(f"Announced as host in room {self.room}")
            except Exception as e:
                print(f"Error announcing host: {e}")

    def send_signal(self, target_id: str, signal_data: dict):
        """
        Отправляет сигнал (offer, answer, ice_candidate) другому клиенту через сервер.
        :param target_id: ID клиента-получателя.
        :param signal_data: Словарь с данными сигнала (sdp или candidate).
        """
        if not self.room:
            print("Error: Not in a room")
            return
            
        payload = {
            'sender': self.client_id,
            'target': target_id,
            'room': self.room,
            'type': signal_data.get('type'),
            'data': signal_data
        }
        print(f"Sending signal to {target_id} via server: {signal_data.get('type')}")
        try:
            self.sio.emit('signal', payload)
        except Exception as e:
            print(f"Error sending signal: {e}")

    def found_host(self, host_id: str):
        """Вызывается, когда найден доступный хост"""
        print(f"Found host callback: {host_id}")
        if self.found_host_callback:
            self.found_host_callback(host_id)

# --- Пример использования (для тестирования отдельно) ---
if __name__ == "__main__":
    def my_signal_handler(data):
        print("App received signal:", data.get('type', 'unknown'))

    def my_host_handler(host_id):
        print("App found host:", host_id)

    client = SignalingClient(on_signal=my_signal_handler)
    client.found_host_callback = my_host_handler
    client.connect()
    client.join_room("test_room")

    # Чтобы скрипт не завершался
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client.sio.disconnect()