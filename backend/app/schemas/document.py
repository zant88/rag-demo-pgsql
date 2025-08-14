"""Pydantic schemas for document models."""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentBase(BaseModel):
    """Base document schema with common fields."""
    original_filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    upload_status: Optional[str] = None
    processing_status: Optional[Dict[str, Any]] = None
    chunk_count: Optional[int] = None
    total_chunks: Optional[int] = None
    extracted_text: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class DocumentInDBBase(DocumentBase):
    """Base schema for document in database."""
    id: int
    filename: str
    file_path: str
    upload_status: str
    processing_status: Optional[Dict[str, Any]] = None
    chunk_count: int
    total_chunks: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentResponse(DocumentInDBBase):
    """Schema for document response."""
    extracted_text: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class DocumentListResponse(DocumentInDBBase):
    """Schema for document list response (minimal fields)."""
    pass


class DocumentStatusResponse(BaseModel):
    """Schema for document status response."""
    document_id: int
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    processing_steps: Optional[Dict[str, Any]] = None
