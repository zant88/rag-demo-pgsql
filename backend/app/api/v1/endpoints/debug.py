"""Debug endpoints for troubleshooting document processing issues."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.document_service import DocumentService

# Create router
router = APIRouter()


@router.get("/documents")
async def debug_documents(
    limit: int = Query(10, description="Number of documents to return"),
    db: Session = Depends(get_db)
):
    """Get recent documents with their processing status."""
    documents = db.query(Document).order_by(desc(Document.created_at)).limit(limit).all()
    
    result = []
    for doc in documents:
        result.append({
            "id": doc.id,
            "filename": doc.original_filename,
            "upload_status": doc.upload_status,
            "processing_status": doc.processing_status,
            "chunk_count": doc.chunk_count,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "created_at": doc.created_at,
            "extracted_text_preview": doc.extracted_text[:500] if doc.extracted_text else None
        })
    
    return {"documents": result}


@router.get("/document/{document_id}")
async def debug_document_details(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get chunks for this document
    chunks = db.query(Chunk).filter(Chunk.document_id == document_id).order_by(Chunk.chunk_index).all()
    
    chunk_info = []
    for chunk in chunks:
        chunk_info.append({
            "id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "content_preview": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
            "word_count": chunk.word_count,
            "char_count": chunk.char_count,
            "processing_status": chunk.processing_status,
            "has_embedding": chunk.embedding is not None and len(chunk.embedding) > 0
        })
    
    return {
        "document": {
            "id": document.id,
            "filename": document.original_filename,
            "file_path": document.file_path,
            "upload_status": document.upload_status,
            "processing_status": document.processing_status,
            "chunk_count": document.chunk_count,
            "total_chunks": document.total_chunks,
            "file_size": document.file_size,
            "mime_type": document.mime_type,
            "created_at": document.created_at,
            "extracted_text_preview": document.extracted_text[:1000] if document.extracted_text else None
        },
        "chunks": chunk_info
    }


@router.get("/search-content")
async def debug_search_content(
    query: str = Query(..., description="Search term to look for in chunks"),
    limit: int = Query(10, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Search for specific content in processed chunks."""
    chunks = db.query(Chunk).filter(
        Chunk.content.ilike(f"%{query}%")
    ).limit(limit).all()
    
    results = []
    for chunk in chunks:
        # Get document info
        document = db.query(Document).filter(Document.id == chunk.document_id).first()
        
        results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_filename": document.original_filename if document else "Unknown",
            "chunk_index": chunk.chunk_index,
            "content_preview": chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content,
            "word_count": chunk.word_count,
            "has_embedding": chunk.embedding is not None and len(chunk.embedding) > 0
        })
    
    return {
        "query": query,
        "total_results": len(results),
        "results": results
    }


@router.post("/reprocess-document/{document_id}")
async def debug_reprocess_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Reprocess a failed document for debugging."""
    document_service = DocumentService(db)
    document = document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        # Delete existing chunks
        db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        db.commit()
        
        # Reset document status
        document.upload_status = "uploaded"
        document.processing_status = {"step": "ready_for_reprocessing", "progress": 0}
        document.chunk_count = 0
        db.commit()
        
        # Reprocess the document
        await document_service.process_document(document_id)
        
        return {"message": f"Document {document_id} reprocessing initiated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")


@router.get("/processing-stats")
async def debug_processing_stats(
    db: Session = Depends(get_db)
):
    """Get overall processing statistics."""
    total_docs = db.query(Document).count()
    completed_docs = db.query(Document).filter(Document.upload_status == "completed").count()
    failed_docs = db.query(Document).filter(Document.upload_status == "failed").count()
    processing_docs = db.query(Document).filter(Document.upload_status == "processing").count()
    
    total_chunks = db.query(Chunk).count()
    chunks_with_embeddings = db.query(Chunk).filter(Chunk.embedding.isnot(None)).count()
    
    # Get recent failed documents
    failed_documents = db.query(Document).filter(
        Document.upload_status == "failed"
    ).order_by(desc(Document.created_at)).limit(5).all()
    
    failed_info = []
    for doc in failed_documents:
        failed_info.append({
            "id": doc.id,
            "filename": doc.original_filename,
            "error": doc.processing_status.get("error") if doc.processing_status else "Unknown error",
            "created_at": doc.created_at
        })
    
    return {
        "documents": {
            "total": total_docs,
            "completed": completed_docs,
            "failed": failed_docs,
            "processing": processing_docs
        },
        "chunks": {
            "total": total_chunks,
            "with_embeddings": chunks_with_embeddings
        },
        "recent_failures": failed_info
    }