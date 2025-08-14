"""Chat API endpoints for querying documents."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.chat import ChatMessage, ChatResponse
from app.services.chat_service import ChatService

# Create router
router = APIRouter()


class ChatRequest(BaseModel):
    """Schema for chat request."""
    query: str
    document_ids: Optional[List[int]] = None  # Limit search to specific documents
    use_graph_search: bool = False  # Enable graph-based search
    conversation_history: Optional[List[ChatMessage]] = None  # Previous conversation context
    

@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Process a chat query using RAG pipeline."""
    try:
        chat_service = ChatService(db)
        response = await chat_service.process_query(
            query=request.query,
            document_ids=request.document_ids,
            use_graph_search=request.use_graph_search,
            conversation_history=request.conversation_history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/query-stream")
async def chat_query_stream(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Process a chat query and stream the response."""
    try:
        chat_service = ChatService(db)
        # This would return a streaming response
        # Implementation would depend on specific requirements
        return {"message": "Streaming endpoint not yet implemented"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
