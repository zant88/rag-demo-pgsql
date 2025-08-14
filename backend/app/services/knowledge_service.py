"""Knowledge service for handling manual knowledge entries."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeEntry
from app.schemas.knowledge import KnowledgeCreate, KnowledgeUpdate

from app.models.chunk import Chunk
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService

class KnowledgeService:
    """Service for managing manual knowledge entries."""
    def __init__(self, db: Session):
        self.db = db
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()

    async def create_manual_knowledge(self, knowledge_data: KnowledgeCreate) -> KnowledgeEntry:
        entry = KnowledgeEntry(
            title=knowledge_data.title,
            summary=knowledge_data.summary,
            content=knowledge_data.content,
            keywords=knowledge_data.keywords,
            categories=knowledge_data.categories,
            source=knowledge_data.source,
            author=knowledge_data.author,
            date=knowledge_data.date,
            chunk_count=0,
            processing_status="pending"
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)

        # Chunk and embed the manual knowledge content
        try:
            chunks = await self.chunking_service.chunk_text(entry.content)
            embeddings = []
            for chunk_text in chunks:
                embedding = await self.embedding_service.generate_embedding(chunk_text)
                embeddings.append(embedding)

            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = Chunk(
                    document_id=None,
                    knowledge_entry_id=entry.id,
                    chunk_index=i,
                    content=chunk_text,
                    content_cleaned=chunk_text,
                    embedding=embedding,
                    word_count=len(chunk_text.split()),
                    char_count=len(chunk_text),
                    processing_status="processed"
                )
                self.db.add(chunk)
            entry.chunk_count = len(chunks)
            entry.processing_status = "processed"
            self.db.commit()
            self.db.refresh(entry)
        except Exception as e:
            entry.processing_status = f"failed: {str(e)}"
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def get_knowledge_entries(self, skip: int = 0, limit: int = 100) -> List[KnowledgeEntry]:
        return (
            self.db.query(KnowledgeEntry)
            .order_by(KnowledgeEntry.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_knowledge_entry(self, entry_id: int) -> Optional[KnowledgeEntry]:
        return self.db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()

    def delete_knowledge_entry(self, entry_id: int) -> bool:
        entry = self.db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id).first()
        if not entry:
            return False
        self.db.delete(entry)
        self.db.commit()
        return True
