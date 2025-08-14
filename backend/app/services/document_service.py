"""Document service for handling document processing and management."""

import os
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.text_extraction_service import TextExtractionService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.core.config import settings


class DocumentService:
    """Service for managing documents and their processing."""
    
    def __init__(self, db: Session):
        self.db = db
        self.text_extraction_service = TextExtractionService()
        self.chunking_service = ChunkingService()
        self.embedding_service = EmbeddingService()
    
    def create_document(self, document_data: DocumentCreate) -> Document:
        """Create a new document record."""
        # Generate unique filename
        file_extension = os.path.splitext(document_data.original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        db_document = Document(
            filename=unique_filename,
            original_filename=document_data.original_filename,
            file_path="",  # Will be set later
            file_size=document_data.file_size or 0,
            mime_type=document_data.mime_type,
            upload_status="uploading",
            processing_status={"step": "upload", "progress": 0}
        )
        
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        
        return db_document
    
    def update_document_path(self, document_id: int, file_path: str) -> bool:
        """Update the file path for a document."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.file_path = file_path
            document.upload_status = "uploaded"
            document.processing_status = {"step": "uploaded", "progress": 100}
            self.db.commit()
            return True
        return False
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get a list of documents."""
        return (
            self.db.query(Document)
            .order_by(desc(Document.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def delete_document(self, document_id: int) -> bool:
        """Delete a document and its chunks."""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        # Delete associated chunks
        self.db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        
        # Delete the document file if it exists
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except OSError:
                pass  # File might already be deleted
        
        # Delete the document record
        self.db.delete(document)
        self.db.commit()
        
        return True
    
    async def process_document(self, document_id: int, client_id: str = None):
        """Process a document through the full pipeline."""
        document = self.get_document(document_id)
        if not document:
            print(f"[ERROR] Document {document_id} not found")
            return
        
        print(f"[INFO] Starting processing for document {document_id}: {document.original_filename}")
        
        try:
            # Update status to processing
            document.upload_status = "processing"
            document.processing_status = {"step": "text_extraction", "progress": 10}
            self.db.commit()
            
            # Step 1: Extract text
            print(f"[INFO] Extracting text from {document.file_path} (MIME: {document.mime_type})")
            extracted_text = await self.text_extraction_service.extract_text(
                document.file_path, 
                document.mime_type
            )
            if not extracted_text or len(extracted_text.strip()) == 0:
                raise Exception(f"No text extracted from document {document.original_filename}. File may be corrupted, password-protected, or contain only images.")
            
            print(f"[DEBUG] Extracted text length: {len(extracted_text)}")
            print(f"[DEBUG] First 200 chars: {extracted_text[:200]}...")
            
            # Store extracted text preview for debugging
            document.extracted_text = extracted_text[:10000]  # Store first 10k chars for debugging
            document.processing_status = {"step": "text_cleaning", "progress": 30}
            self.db.commit()
            
            # Step 2: Clean text
            print(f"[INFO] Cleaning extracted text")
            cleaned_text = await self.text_extraction_service.clean_text(extracted_text)
            print(f"[DEBUG] Cleaned text length: {len(cleaned_text)}")
            
            if len(cleaned_text.strip()) == 0:
                raise Exception(f"Text cleaning resulted in empty content for {document.original_filename}")
            
            # Step 3: Chunk text
            print(f"[INFO] Chunking text into smaller segments")
            document.processing_status = {"step": "chunking", "progress": 50}
            self.db.commit()
            
            chunks = await self.chunking_service.chunk_text(cleaned_text)
            print(f"[DEBUG] Chunk count: {len(chunks)}")
            
            if len(chunks) == 0:
                raise Exception(f"Text chunking resulted in no chunks for {document.original_filename}")
            
            # Check if document exceeds chunk limit
            if len(chunks) > settings.MAX_CHUNKS_PER_BATCH:
                print(f"[INFO] Document has {len(chunks)} chunks, exceeding limit of {settings.MAX_CHUNKS_PER_BATCH}. Processing in batches.")
                await self._process_document_in_batches(document, chunks, client_id)
                return
            
            # Log sample chunks for debugging
            for i, chunk in enumerate(chunks[:3]):
                print(f"[DEBUG] Sample chunk {i}: {chunk[:100]}...")
            
            # Step 4: Generate embeddings and store chunks
            print(f"[INFO] Generating embeddings for {len(chunks)} chunks")
            document.processing_status = {"step": "embedding", "progress": 70}
            self.db.commit()
            
            successful_chunks = 0
            for i, chunk_text in enumerate(chunks):
                try:
                    print(f"[DEBUG] Processing chunk {i+1}/{len(chunks)}, length: {len(chunk_text)}")
                    
                    # Generate embedding
                    embedding = await self.embedding_service.generate_embedding(chunk_text)
                    
                    if not embedding or len(embedding) == 0:
                        print(f"[WARNING] Empty embedding generated for chunk {i}")
                        continue
                    
                    # Create chunk record
                    chunk = Chunk(
                        document_id=document.id,
                        chunk_index=i,
                        content=chunk_text,
                        content_cleaned=chunk_text,  # Already cleaned
                        embedding=embedding,
                        word_count=len(chunk_text.split()),
                        char_count=len(chunk_text),
                        processing_status="processed"
                    )
                    
                    self.db.add(chunk)
                    successful_chunks += 1
                    
                except Exception as chunk_error:
                    print(f"[ERROR] Failed to process chunk {i}: {chunk_error}")
                    continue
            
            if successful_chunks == 0:
                raise Exception(f"No chunks were successfully processed for {document.original_filename}")
            
            # Update document status
            document.upload_status = "completed"
            document.chunk_count = successful_chunks
            document.total_chunks = len(chunks)
            document.processing_status = {"step": "completed", "progress": 100}
            
            self.db.commit()
            print(f"[SUCCESS] Document {document_id} ({document.original_filename}) processing complete. Successfully processed {successful_chunks}/{len(chunks)} chunks")
            
            # WebSocket notification (if client_id provided)
            if client_id:
                try:
                    from app.api.v1.endpoints.websocket_utils import notify_processing_complete
                    import asyncio
                    await notify_processing_complete(client_id, document.id, document.original_filename)
                except Exception as notify_exc:
                    print(f"[WebSocket Notify Error] {notify_exc}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Exception during processing of doc {document_id} ({document.original_filename}): {error_msg}")
            print(f"[ERROR] Document path: {document.file_path}")
            print(f"[ERROR] Document MIME type: {document.mime_type}")
            
            # Update status to failed with detailed error info
            document.upload_status = "failed"
            document.processing_status = {
                "step": "error", 
                "error": error_msg,
                "progress": 0,
                "file_path": document.file_path,
                "mime_type": document.mime_type,
                "timestamp": str(func.now())
            }
            self.db.commit()
            
            # Re-raise the exception for debugging
            raise e
    
    async def _process_document_in_batches(self, document: Document, chunks: List[str], client_id: str = None):
        """Process large documents in smaller batches to avoid memory and processing limits."""
        total_chunks = len(chunks)
        total_batches = (total_chunks + settings.MAX_CHUNKS_PER_BATCH - 1) // settings.MAX_CHUNKS_PER_BATCH
        
        print(f"[INFO] Processing {total_chunks} chunks in {total_batches} batches")
        
        successful_chunks = 0
        
        try:
            for batch_num in range(total_batches):
                start_idx = batch_num * settings.MAX_CHUNKS_PER_BATCH
                end_idx = min(start_idx + settings.MAX_CHUNKS_PER_BATCH, total_chunks)
                batch_chunks = chunks[start_idx:end_idx]
                
                print(f"[INFO] Processing batch {batch_num + 1}/{total_batches} (chunks {start_idx + 1}-{end_idx})")
                
                # Update progress
                progress = int((batch_num / total_batches) * 30 + 70)  # 70-100% range
                document.processing_status = {
                    "step": "embedding_batch", 
                    "progress": progress,
                    "batch": batch_num + 1,
                    "total_batches": total_batches
                }
                self.db.commit()
                
                # Process chunks in this batch
                batch_successful = await self._process_chunk_batch(document, batch_chunks, start_idx)
                successful_chunks += batch_successful
                
                print(f"[INFO] Batch {batch_num + 1} completed: {batch_successful}/{len(batch_chunks)} chunks processed")
                
                # Small delay between batches to prevent overwhelming the system
                if batch_num < total_batches - 1:  # Don't delay after the last batch
                    import asyncio
                    await asyncio.sleep(1)
            
            if successful_chunks == 0:
                raise Exception(f"No chunks were successfully processed for {document.original_filename}")
            
            # Update document status
            document.upload_status = "completed"
            document.chunk_count = successful_chunks
            document.total_chunks = total_chunks
            document.processing_status = {"step": "completed", "progress": 100}
            
            self.db.commit()
            print(f"[SUCCESS] Document {document.id} ({document.original_filename}) batch processing complete. Successfully processed {successful_chunks}/{total_chunks} chunks")
            
            # WebSocket notification (if client_id provided)
            if client_id:
                try:
                    from app.api.v1.endpoints.websocket_utils import notify_processing_complete
                    import asyncio
                    await notify_processing_complete(client_id, document.id, document.original_filename)
                except Exception as notify_exc:
                    print(f"[WebSocket Notify Error] {notify_exc}")
                    
        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            
            document.upload_status = "failed"
            document.processing_status = {
                "step": "error", 
                "error": error_msg,
                "progress": 0
            }
            self.db.commit()
            
            if client_id:
                try:
                    from app.api.v1.endpoints.websocket_utils import notify_processing_error
                    import asyncio
                    await notify_processing_error(client_id, document.id, document.original_filename, error_msg)
                except Exception as notify_exc:
                    print(f"[WebSocket Notify Error] {notify_exc}")
    
    async def _process_chunk_batch(self, document: Document, batch_chunks: List[str], start_idx: int) -> int:
        """Process a batch of chunks and return the number of successfully processed chunks."""
        successful_chunks = 0
        
        for i, chunk_text in enumerate(batch_chunks):
            try:
                chunk_index = start_idx + i
                print(f"[DEBUG] Processing chunk {chunk_index + 1}, length: {len(chunk_text)}")
                
                # Generate embedding
                embedding = await self.embedding_service.generate_embedding(chunk_text)
                
                if not embedding or len(embedding) == 0:
                    print(f"[WARNING] Empty embedding generated for chunk {chunk_index}")
                    continue
                
                # Create chunk record
                chunk = Chunk(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    content=chunk_text,
                    content_cleaned=chunk_text,  # Already cleaned
                    embedding=embedding,
                    word_count=len(chunk_text.split()),
                    char_count=len(chunk_text),
                    processing_status="processed"
                )
                
                self.db.add(chunk)
                successful_chunks += 1
                
                # Commit every 100 chunks to avoid large transactions
                if (i + 1) % 100 == 0:
                    self.db.commit()
                    print(f"[DEBUG] Committed batch progress: {i + 1} chunks")
                
            except Exception as chunk_error:
                print(f"[ERROR] Failed to process chunk {start_idx + i}: {chunk_error}")
                continue
        
        # Final commit for remaining chunks
        self.db.commit()
        return successful_chunks
    
    async def assemble_and_process_document(self, document_id: str, total_chunks: int, client_id: str = None):
        """Assemble chunked upload and process the document."""
        try:
            print(f"[DEBUG] Starting assembly for doc {document_id} with {total_chunks} chunks")
            document = self.get_document(int(document_id))
            if not document:
                print(f"[ERROR] Document {document_id} not found during assembly.")
                return

            file_extension = os.path.splitext(document.original_filename)[1]
            final_path = os.path.join(
                settings.UPLOAD_FOLDER,
                f"{document_id}{file_extension}"
            )

            # Combine all chunks
            with open(final_path, "wb") as final_file:
                for chunk_index in range(total_chunks):
                    chunk_filename = f"{document_id}_chunk_{chunk_index}"
                    chunk_path = os.path.join(settings.UPLOAD_FOLDER, chunk_filename)
                    if os.path.exists(chunk_path):
                        with open(chunk_path, "rb") as chunk_file:
                            chunk_data = chunk_file.read()
                            print(f"[DEBUG] Writing chunk {chunk_index} ({len(chunk_data)} bytes)")
                            final_file.write(chunk_data)
                        os.remove(chunk_path)
                    else:
                        print(f"[ERROR] Missing chunk file: {chunk_path}")
            assembled_size = os.path.getsize(final_path)
            print(f"[DEBUG] Assembly complete for doc {document_id}, final size: {assembled_size} bytes")

            # Update document path and process
            self.update_document_path(int(document_id), final_path)
            await self.process_document(int(document_id), client_id=client_id)

        except Exception as e:
            print(f"[ERROR] Exception during assembly of doc {document_id}: {e}")
            document = self.get_document(int(document_id))
            if document:
                document.upload_status = "failed"
                document.processing_status = {
                    "step": "assembly_error",
                    "error": str(e)
                }
                self.db.commit()
                self.db.commit()
