#!/usr/bin/env python3
"""Test script to debug document processing issues."""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.document_service import DocumentService
from app.services.text_extraction_service import TextExtractionService
from sqlalchemy import desc


async def test_text_extraction(file_path: str):
    """Test text extraction from a specific file."""
    print(f"\n=== Testing Text Extraction ===")
    print(f"File: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} does not exist")
        return None
    
    # Determine MIME type based on extension
    ext = Path(file_path).suffix.lower()
    mime_type_map = {
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc': 'application/msword',
        '.txt': 'text/plain'
    }
    mime_type = mime_type_map.get(ext, 'application/octet-stream')
    print(f"MIME Type: {mime_type}")
    
    # Extract text
    text_service = TextExtractionService()
    try:
        extracted_text = await text_service.extract_text(file_path, mime_type)
        if extracted_text:
            print(f"Extracted text length: {len(extracted_text)}")
            print(f"First 500 characters:")
            print("-" * 50)
            print(extracted_text[:500])
            print("-" * 50)
            
            # Check for SNBT content
            if 'SNBT' in extracted_text.upper():
                print("✓ SNBT content found in extracted text!")
                # Find and show SNBT occurrences
                lines = extracted_text.split('\n')
                snbt_lines = [line for line in lines if 'SNBT' in line.upper()]
                print(f"Found {len(snbt_lines)} lines containing SNBT:")
                for i, line in enumerate(snbt_lines[:5]):  # Show first 5
                    print(f"  {i+1}: {line.strip()}")
            else:
                print("✗ No SNBT content found in extracted text")
                
            return extracted_text
        else:
            print("ERROR: No text extracted")
            return None
    except Exception as e:
        print(f"ERROR during text extraction: {e}")
        return None


async def check_database_content():
    """Check what's currently in the database."""
    print(f"\n=== Database Content Check ===")
    
    db = SessionLocal()
    try:
        # Get recent documents
        documents = db.query(Document).order_by(desc(Document.created_at)).limit(10).all()
        print(f"Found {len(documents)} recent documents:")
        
        for doc in documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"  Filename: {doc.original_filename}")
            print(f"  Status: {doc.upload_status}")
            print(f"  Chunks: {doc.chunk_count}")
            print(f"  File path: {doc.file_path}")
            
            if doc.processing_status:
                print(f"  Processing status: {doc.processing_status}")
            
            # Check if file still exists
            if doc.file_path and os.path.exists(doc.file_path):
                print(f"  ✓ File exists on disk")
            else:
                print(f"  ✗ File missing from disk")
        
        # Search for SNBT content in chunks
        print(f"\n=== SNBT Content Search ===")
        snbt_chunks = db.query(Chunk).filter(
            Chunk.content.ilike('%SNBT%')
        ).limit(10).all()
        
        print(f"Found {len(snbt_chunks)} chunks containing SNBT")
        for chunk in snbt_chunks:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            print(f"\nChunk ID: {chunk.id} (Document: {doc.original_filename if doc else 'Unknown'})")
            print(f"  Content preview: {chunk.content[:200]}...")
        
        # Search for "KETENTUAN" content
        print(f"\n=== KETENTUAN Content Search ===")
        ketentuan_chunks = db.query(Chunk).filter(
            Chunk.content.ilike('%KETENTUAN%')
        ).limit(5).all()
        
        print(f"Found {len(ketentuan_chunks)} chunks containing KETENTUAN")
        for chunk in ketentuan_chunks:
            doc = db.query(Document).filter(Document.id == chunk.document_id).first()
            print(f"\nChunk ID: {chunk.id} (Document: {doc.original_filename if doc else 'Unknown'})")
            print(f"  Content preview: {chunk.content[:200]}...")
            
    finally:
        db.close()


async def test_document_reprocessing(document_id: int):
    """Test reprocessing a specific document."""
    print(f"\n=== Testing Document Reprocessing ===")
    print(f"Document ID: {document_id}")
    
    db = SessionLocal()
    try:
        document_service = DocumentService(db)
        document = document_service.get_document(document_id)
        
        if not document:
            print(f"ERROR: Document {document_id} not found")
            return
        
        print(f"Document: {document.original_filename}")
        print(f"Current status: {document.upload_status}")
        print(f"File path: {document.file_path}")
        
        # Check if file exists
        if not os.path.exists(document.file_path):
            print(f"ERROR: File {document.file_path} does not exist")
            return
        
        # Delete existing chunks
        print("Deleting existing chunks...")
        db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        db.commit()
        
        # Reset document status
        document.upload_status = "uploaded"
        document.processing_status = {"step": "ready_for_reprocessing", "progress": 0}
        document.chunk_count = 0
        db.commit()
        
        # Reprocess
        print("Starting reprocessing...")
        await document_service.process_document(document_id)
        
        print("Reprocessing completed!")
        
    except Exception as e:
        print(f"ERROR during reprocessing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


async def main():
    """Main test function."""
    print("RAG Document Processing Debug Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_document_processing.py check          - Check database content")
        print("  python test_document_processing.py extract <file> - Test text extraction")
        print("  python test_document_processing.py reprocess <id> - Reprocess document")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        await check_database_content()
    
    elif command == "extract" and len(sys.argv) > 2:
        file_path = sys.argv[2]
        await test_text_extraction(file_path)
    
    elif command == "reprocess" and len(sys.argv) > 2:
        try:
            document_id = int(sys.argv[2])
            await test_document_reprocessing(document_id)
        except ValueError:
            print("ERROR: Document ID must be a number")
    
    else:
        print("Invalid command or missing arguments")


if __name__ == "__main__":
    asyncio.run(main())