"""Main API router for v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import documents, chat, knowledge, websocket_notify, debug

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(websocket_notify.router, tags=["websocket"])
api_router.include_router(debug.router, prefix="/debug", tags=["debug"])


# Health check endpoint
@api_router.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}
