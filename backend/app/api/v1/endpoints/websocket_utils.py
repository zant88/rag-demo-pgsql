from typing import Optional
from .websocket_notify import manager
import asyncio

async def notify_processing_complete(client_id: str, document_id: int, filename: str):
    message = {
        "event": "processing_complete",
        "document_id": document_id,
        "filename": filename
    }
    await manager.send_personal_message(message, client_id)
