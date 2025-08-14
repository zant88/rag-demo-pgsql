from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from starlette.websockets import WebSocketState

router = APIRouter()

# In-memory connection manager for demo (for production, use Redis/pubsub)
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: dict, client_id: str):
        ws = self.active_connections.get(client_id)
        if ws and ws.application_state == WebSocketState.CONNECTED:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in self.active_connections.values():
            if ws.application_state == WebSocketState.CONNECTED:
                await ws.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/processing/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(client_id)
