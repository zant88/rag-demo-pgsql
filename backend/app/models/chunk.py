"""Chunk model for storing document chunks and embeddings."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Chunk(Base):
    """Model representing a chunk of text from a document."""
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    knowledge_entry_id = Column(Integer, ForeignKey("knowledge_entries.id"), nullable=True)
    chunk_index = Column(Integer, nullable=False)  # Position of chunk in document
    content = Column(Text, nullable=False)  # The actual text content
    content_cleaned = Column(Text)  # Cleaned version of content
    
    # Embedding vector (default to 1536 dimensions for Cohere embeddings)
    embedding = Column(Vector(1536))
    
    # Metadata
    metadata_json = Column(JSON)  # Chunk-specific metadata
    word_count = Column(Integer)
    char_count = Column(Integer)
    
    # Processing status
    processing_status = Column(String, default="pending")  # pending, processed, failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    knowledge_entry = relationship("KnowledgeEntry", backref="chunks")
    
    def __repr__(self):
        return f"<Chunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"


# Create an index on the embedding column for faster similarity searches
Index("idx_chunks_embedding", Chunk.embedding, postgresql_using="ivfflat")
