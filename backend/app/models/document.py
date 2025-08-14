"""Document model for storing document metadata."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy.orm import relationship


class Document(Base):
    """Model representing a document in the system."""
    __tablename__ = "documents"

    # Relationship to chunks
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    upload_status = Column(String, default="processing")  # processing, completed, failed
    processing_status = Column(JSON)  # Detailed status of processing steps
    chunk_count = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    extracted_text = Column(Text)  # Store extracted text for small documents
    metadata_json = Column(JSON)  # Document metadata (author, title, etc.)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.original_filename}', status='{self.upload_status}')>"
