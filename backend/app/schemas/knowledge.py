"""Pydantic schemas for knowledge models."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class KnowledgeBase(BaseModel):
    """Base knowledge schema with common fields."""
    title: str
    summary: Optional[str] = None
    content: str
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    source: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None


class KnowledgeCreate(KnowledgeBase):
    """Schema for creating a new knowledge entry."""
    pass


class KnowledgeUpdate(BaseModel):
    """Schema for updating a knowledge entry."""
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    source: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None


class KnowledgeInDBBase(KnowledgeBase):
    """Base schema for knowledge in database."""
    id: int
    chunk_count: int
    processing_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KnowledgeResponse(KnowledgeInDBBase):
    """Schema for knowledge response."""
    metadata_json: Optional[Dict[str, Any]] = None
