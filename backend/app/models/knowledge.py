"""Knowledge model for storing manual knowledge entries."""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ARRAY
from sqlalchemy.sql import func
from app.core.database import Base


class KnowledgeEntry(Base):
    """Model representing a manual knowledge entry."""
    __tablename__ = "knowledge_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    summary = Column(Text)
    content = Column(Text, nullable=False)
    keywords = Column(ARRAY(String))  # Array of keywords
    categories = Column(ARRAY(String))  # Array of categories
    source = Column(String)
    author = Column(String)
    date = Column(String)  # Store as string for flexibility
    
    # Processing information
    chunk_count = Column(Integer, default=0)
    processing_status = Column(String, default="pending")  # pending, processed, failed
    metadata_json = Column(JSON)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<KnowledgeEntry(id={self.id}, title='{self.title}', status='{self.processing_status}')>"
