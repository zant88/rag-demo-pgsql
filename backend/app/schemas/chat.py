"""Pydantic schemas for chat models."""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Schema for a chat message."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime


class SourceReference(BaseModel):
    """Schema for a source reference in the response."""
    document_id: int
    document_title: str
    filename: str
    chunk_id: Optional[int] = None
    page_number: Optional[int] = None
    author: Optional[str] = None
    date: Optional[str] = None
    section_header: Optional[str] = None
    relevance_score: Optional[float] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    query: str
    response: str
    sources: List[SourceReference]
    timestamp: datetime
    processing_time: float  # Time taken to process the query
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class ChatHistory(BaseModel):
    """Schema for chat history."""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
