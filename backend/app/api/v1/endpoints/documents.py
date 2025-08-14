"""Documents API endpoints for file upload and management."""

import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentListResponse
from app.services.document_service import DocumentService

# Create router
router = APIRouter()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)


def get_document_service(db: Session = Depends(get_db)):
    """Dependency to get document service instance."""
    return DocumentService(db)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    client_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Upload a document file for processing."""
    try:
        # Create document record
        document_data = DocumentCreate(
            original_filename=file.filename,
            file_size=file.size if hasattr(file, 'size') else 0,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        document_service = DocumentService(db)
        document = document_service.create_document(document_data)
        
        # Save file
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        file_path = os.path.join(settings.UPLOAD_FOLDER, f"{document.id}{file_extension}")
        
        # Save file content
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update document with file path
        document_service.update_document_path(document.id, file_path)
        
        # Process document in background, pass client_id for websocket notification
        background_tasks.add_task(document_service.process_document, document.id, client_id)
        
        return document
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-chunked")
async def upload_chunked_document(
    file_chunk: UploadFile = File(...),
    document_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    client_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Upload a chunk of a document for resumable upload support."""
    try:
        document_service = DocumentService(db)
        
        # If this is the first chunk, create document record
        if chunk_index == 0:
            document_data = DocumentCreate(
                original_filename=filename,
                file_size=0,  # Will be updated later
                mime_type="application/octet-stream"
            )
            document = document_service.create_document(document_data)
            document_id = str(document.id)
        
        # Save chunk
        chunk_filename = f"{document_id}_chunk_{chunk_index}"
        chunk_path = os.path.join(settings.UPLOAD_FOLDER, chunk_filename)
        
        with open(chunk_path, "wb") as buffer:
            content = await file_chunk.read()
            buffer.write(content)
        
        # If this is the last chunk, assemble and process in background
        if chunk_index == total_chunks - 1:
            background_tasks.add_task(document_service.assemble_and_process_document, document_id, total_chunks, client_id)
        
        return {
            "document_id": document_id,
            "chunk_index": chunk_index,
            "status": "uploaded",
            "message": f"Chunk {chunk_index + 1}/{total_chunks} uploaded successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chunk upload failed: {str(e)}")


@router.get("/status/{document_id}", response_model=DocumentResponse)
async def get_document_status(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get the processing status of a document."""
    document_service = DocumentService(db)
    document = document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.get("/list", response_model=List[DocumentListResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all documents with basic information."""
    document_service = DocumentService(db)
    documents = document_service.get_documents(skip=skip, limit=limit)
    return documents


@router.delete("/delete/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and its associated chunks."""
    document_service = DocumentService(db)
    success = document_service.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}
