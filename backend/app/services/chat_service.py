"""Chat service for handling RAG queries and responses."""

import time
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.knowledge import KnowledgeEntry
from app.schemas.chat import ChatResponse, SourceReference, ChatMessage
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from fastapi import HTTPException


class ChatService:
    """Service for processing chat queries using RAG pipeline."""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
    
    async def process_query(
        self, 
        query: str, 
        document_ids: Optional[List[int]] = None,
        use_graph_search: bool = False,
        top_k: int = 5,
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:
        """Process a chat query using the RAG pipeline."""
        start_time = time.time()
        
        try:
            # Step 1: Enhance query with conversation context
            enhanced_query = self._enhance_query_with_context(query, conversation_history)
            print(f"[CONTEXT DEBUG] Original query: {query}")
            print(f"[CONTEXT DEBUG] Enhanced query: {enhanced_query}")
            
            # Step 2: Generate query embedding
            print("[RAG DEBUG] BEFORE EMBEDDING GENERATION")
            query_embedding = await self.embedding_service.generate_query_embedding(enhanced_query)
            # print("[RAG DEBUG] Query embedding:", query_embedding)
            # print("[RAG DEBUG] Query embedding length:", len(query_embedding))
            if not query_embedding:
                raise Exception("Failed to generate query embedding")
            
            # Step 2: Perform semantic search
            relevant_chunks = await self._semantic_search(
                query_embedding, 
                document_ids, 
                7  # Reduced from 15 to stay within Groq's token limits
            )
            # Debug print: Check embedding dimension of first retrieved chunk
            if relevant_chunks:
                # Assuming the embedding is not returned by default in the chunk tuple,
                # fetch it directly from the DB using the chunk id for the first chunk
                first_chunk_id = relevant_chunks[0][0]
                chunk_obj = self.db.query(Chunk).filter(Chunk.id == first_chunk_id).first()
                if chunk_obj:
                    emb = chunk_obj.embedding
                    print(f"[RAG DEBUG] First chunk embedding type: {type(emb)}")
                    try:
                        print(f"[RAG DEBUG] First chunk embedding length: {len(emb)}")
                    except Exception as e:
                        print(f"[RAG DEBUG] Could not get embedding length: {e}")
                    print(f"[RAG DEBUG] First chunk embedding (truncated): {str(emb)[:100]}")
            else:
                print("[RAG DEBUG] No chunks retrieved in semantic search.")
            
            if use_graph_search:
                # TODO: Implement graph-based search
                pass
            
            # Step 5: Prepare context from retrieved chunks
            context = self._prepare_context(relevant_chunks)
            response_text = await self.llm_service.generate_response(query, context)
            
            # Step 6: Prepare source references
            sources = self._prepare_source_references(relevant_chunks)
            
            processing_time = time.time() - start_time
            
            return ChatResponse(
                query=query,
                response=response_text,
                sources=sources,
                timestamp=datetime.now(),
                processing_time=processing_time,
                model_used="groq-llama3-8b-8192"
            )
        
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception in process_query: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
    
    async def _semantic_search(
        self, 
        query_embedding: List[float], 
        document_ids: Optional[List[int]], 
        top_k: int
    ) -> List[tuple]:
        """Perform semantic search using vector similarity."""
        try:
            # Build the SQL query for vector similarity search
            base_query = """
            SELECT 
                c.id,
                c.content,
                c.chunk_index,
                c.metadata_json,
                c.document_id,
                c.knowledge_entry_id,
                (c.embedding <=> (:query_embedding)::vector) as distance
            FROM chunks c
            WHERE c.processing_status = 'processed'
            """
            
            # If document_ids is specified, filter only document chunks
            if document_ids:
                base_query += " AND c.document_id = ANY(:document_ids)"
            # Otherwise, include both document and manual knowledge chunks
            base_query += " ORDER BY c.embedding <=> (:query_embedding)::vector LIMIT :top_k"
            
            # Execute the query
            params = {
                "query_embedding": query_embedding,
                "top_k": top_k
            }
            
            if document_ids:
                params["document_ids"] = document_ids
            
            print("[RAG DEBUG] SQL Query:", base_query)
            print("[RAG DEBUG] Query Params:", params)
            
            result = self.db.execute(text(base_query), params)
            return result.fetchall()
        
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return []
    
    def _enhance_query_with_context(self, query: str, conversation_history: Optional[List[ChatMessage]]) -> str:
        """Enhance the current query with relevant context from conversation history."""
        if not conversation_history or len(conversation_history) == 0:
            return query
        
        # Get the last few messages for context (limit to avoid token overflow)
        recent_messages = conversation_history[-4:]  # Last 4 messages (2 exchanges)
        
        # Extract key entities and topics from recent conversation
        context_parts = []
        for msg in recent_messages:
            if msg.role == "user":
                # Add user queries as context
                context_parts.append(f"Previous question: {msg.content}")
        
        if context_parts:
            # Combine context with current query
            context_str = " ".join(context_parts)
            enhanced_query = f"{context_str}. Current question: {query}"
            return enhanced_query
        
        return query
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens (approximately 4 characters per token)."""
        return len(text) // 4
    
    def _prepare_context(self, chunks: List[tuple]) -> str:
        """Prepare context string from retrieved chunks with token limit consideration."""
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        total_tokens = 0
        max_context_tokens = 4000  # Leave room for system prompt and response
        
        for i, chunk in enumerate(chunks, 1):
            chunk_content = chunk[1]  # content field
            chunk_index = chunk[2]    # chunk_index field
            document_id = chunk[4]
            knowledge_entry_id = chunk[5]
            filename = None
            # Fetch proper filename/title
            if document_id is not None:
                doc = self.db.query(Document).filter(Document.id == document_id).first()
                if doc:
                    filename = doc.original_filename
            elif knowledge_entry_id is not None:
                entry = self.db.query(KnowledgeEntry).filter(KnowledgeEntry.id == knowledge_entry_id).first()
                if entry:
                    filename = entry.title
            
            chunk_text = f"[Source {i}: {filename or 'Manual Knowledge'}, Section {chunk_index + 1}]\n{chunk_content}\n"
            chunk_tokens = self._estimate_tokens(chunk_text)
            
            # Check if adding this chunk would exceed token limit
            if total_tokens + chunk_tokens > max_context_tokens:
                print(f"[TOKEN LIMIT] Stopping at chunk {i-1} to stay within token limits")
                break
                
            context_parts.append(chunk_text)
            total_tokens += chunk_tokens
        
        context = "\n".join(context_parts)
        print(f"[TOKEN COUNT] Estimated context tokens: {self._estimate_tokens(context)}")
        return context
    
    def _prepare_source_references(self, chunks: List[tuple]) -> List[SourceReference]:
        """Prepare source references from retrieved chunks."""
        sources = []
        
        for chunk in chunks:
            chunk_id = chunk[0]
            chunk_content = chunk[1]
            chunk_index = chunk[2]
            chunk_metadata = chunk[3] or {}
            document_id = chunk[4]
            knowledge_entry_id = chunk[5]
            distance = float(chunk[6])

            # If document_id is not None, try to get filename and metadata from document
            filename = None
            document_metadata = {}
            document_title = None
            author = None
            date = None
            if document_id is not None:
                # Try to fetch document info from DB if needed (optional, can be optimized)
                doc = self.db.query(Document).filter(Document.id == document_id).first()
                if doc:
                    filename = doc.original_filename
                    document_metadata = doc.metadata_json or {}
                    document_title = document_metadata.get('title', filename)
                    author = document_metadata.get('author')
                    date = document_metadata.get('date')
            elif knowledge_entry_id is not None:
                # Manual knowledge chunk: fetch title/author/date from KnowledgeEntry
                entry = self.db.query(KnowledgeEntry).filter(KnowledgeEntry.id == knowledge_entry_id).first()
                if entry:
                    filename = entry.title
                    document_title = entry.title
                    author = entry.author
                    date = entry.date

            # Calculate relevance score (inverse of distance)
            relevance_score = 1.0 / (1.0 + distance)

            source = SourceReference(
                document_id=document_id if document_id is not None else knowledge_entry_id,
                document_title=document_title or filename,
                filename=filename,
                chunk_id=chunk_id,
                page_number=chunk_metadata.get('page_number'),
                author=author,
                date=date,
                section_header=chunk_metadata.get('section_header'),
                relevance_score=relevance_score
            )
            sources.append(source)
        
        return sources
