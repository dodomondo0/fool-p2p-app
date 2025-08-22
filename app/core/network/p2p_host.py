# app/core/network/p2p_host.py
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
import json
import logging

logger = logging.getLogger(__name__)

class P2PHost:
    """Хост P2P соединения - управляет соединениями с несколькими клиентами"""
    
    def __init__(self, on_client_message_callback=None):
        self.connections = {}  # {client_id: RTCPeerConnection}
        self.data_channels = {}  # {client_id: RTCDataChannel}
        self.on_client_message_callback = on_client_message_callback
        self.client_ready = {}  # {client_id: bool}
        
    async def create_offer_for_client(self, client_id):
        """Создание оффера для нового клиента"""
        try:
            pc = RTCPeerConnection()
            self.connections[client_id] = pc
            
            # Создаем data channel для клиента
            channel = pc.createDataChannel(f"game_channel_{client_id}")
            self.data_channels[client_id] = channel
            self.client_ready[client_id] = False
            
            # Настраиваем события для соединения
            self._setup_connection_events(client_id, pc)
            self._setup_data_channel_events(client_id, channel)
            
            # Создаем оффер
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            
            logger.info(f"Offer created for client {client_id}")
            return {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
        except Exception as e:
            logger.error(f"Error creating offer for client {client_id}: {e}")
            return None
            
    async def handle_answer_from_client(self, client_id, answer_sdp):
        """Обработка ответа от клиента"""
        try:
            pc = self.connections.get(client_id)
            if not pc:
                logger.error(f"No connection found for client {client_id}")
                return False
                
            await pc.setRemoteDescription(
                RTCSessionDescription(answer_sdp["sdp"], answer_sdp["type"])
            )
            
            logger.info(f"Answer handled from client {client_id}")
            return True
        except Exception as e:
            logger.error(f"Error handling answer from client {client_id}: {e}")
            return False
            
    async def handle_ice_candidate_from_client(self, client_id, candidate_data):
        """Обработка ICE кандидата от клиента"""
        try:
            pc = self.connections.get(client_id)
            if not pc:
                return
                
            from aiortc import RTCIceCandidate
            candidate = RTCIceCandidate(
                sdpMid=candidate_data.get('sdpMid'),
                sdpMLineIndex=candidate_data.get('sdpMLineIndex'),
                candidate=candidate_data.get('candidate')
            )
            await pc.addIceCandidate(candidate)
            logger.info(f"ICE candidate added for client {client_id}")
        except Exception as e:
            logger.error(f"Error handling ICE candidate from client {client_id}: {e}")
            
    def _setup_connection_events(self, client_id, pc):
        """Настройка событий соединения"""
        @pc.on("connectionstatechange")
        def on_connectionstatechange():
            logger.info(f"Connection state for client {client_id}: {pc.connectionState}")
            if pc.connectionState == "connected":
                logger.info(f"Client {client_id} connected successfully")
            elif pc.connectionState in ["failed", "closed", "disconnected"]:
                self._handle_client_disconnect(client_id)
                
        @pc.on("icecandidate")
        def on_icecandidate(candidate):
            if candidate:
                # Отправляем ICE кандидат клиенту через сигнальный сервер
                # Здесь будет вызов callback
                pass
                
    def _setup_data_channel_events(self, client_id, channel):
        """Настройка событий data channel"""
        @channel.on("open")
        def on_open():
            logger.info(f"Data channel opened for client {client_id}")
            self.client_ready[client_id] = True
            
        @channel.on("message")
        def on_message(message):
            logger.info(f"Message received from client {client_id}")
            try:
                data = json.loads(message)
                if self.on_client_message_callback:
                    self.on_client_message_callback(client_id, data)
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON message")
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {e}")
                
        @channel.on("close")
        def on_close():
            logger.info(f"Data channel closed for client {client_id}")
            self.client_ready[client_id] = False
            self._handle_client_disconnect(client_id)
            
    def _handle_client_disconnect(self, client_id):
        """Обработка отключения клиента"""
        logger.info(f"Client {client_id} disconnected")
        # Удаляем соединение и канал
        if client_id in self.connections:
            del self.connections[client_id]
        if client_id in self.data_channels:
            del self.data_channels[client_id]
        if client_id in self.client_ready:
            del self.client_ready[client_id]
            
    def send_message_to_client(self, client_id, message_data):
        """Отправка сообщения конкретному клиенту"""
        channel = self.data_channels.get(client_id)
        if not channel or not self.client_ready.get(client_id, False):
            logger.warning(f"Client {client_id} not ready or channel not available")
            return False
            
        try:
            message_json = json.dumps(message_data, ensure_ascii=False)
            channel.send(message_json)
            logger.info(f"Message sent to client {client_id}: {message_data.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
            return False
            
    def broadcast_message(self, message_data, exclude_client=None):
        """Отправка сообщения всем клиентам"""
        success_count = 0
        for client_id in list(self.data_channels.keys()):
            if client_id != exclude_client:
                if self.send_message_to_client(client_id, message_data):
                    success_count += 1
                    
        logger.info(f"Broadcast message sent to {success_count} clients")
        return success_count
        
    async def close_all_connections(self):
        """Закрытие всех соединений"""
        for client_id, pc in self.connections.items():
            try:
                await pc.close()
                logger.info(f"Connection closed for client {client_id}")
            except Exception as e:
                logger.error(f"Error closing connection for client {client_id}: {e}")
                
        self.connections.clear()
        self.data_channels.clear()
        self.client_ready.clear()