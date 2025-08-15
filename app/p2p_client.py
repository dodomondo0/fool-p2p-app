# app/p2p_client.py
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
import json
import socketio

sio = socketio.Client()

class P2PClient:
    def __init__(self):
        self.pc = RTCPeerConnection()
        self.setup_events()

    def setup_events(self):
        @self.pc.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                print("Received:", message)

    async def create_offer(self):
        channel = self.pc.createDataChannel("game")
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        return offer

    async def handle_offer(self, offer):
        await self.pc.setRemoteDescription(RTCSessionDescription(offer["sdp"], offer["type"]))
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        return answer

    async def handle_answer(self, answer):
        await self.pc.setRemoteDescription(RTCSessionDescription(answer["sdp"], answer["type"]))